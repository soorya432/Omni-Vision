
import time
import threading
from pathlib import Path
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk
import torch

from .config import YOLO_MODEL, YOLO_CONF, OCR_LANGS, OUTPUTS
from .models.detector import Detector
from .models.ocr import OCR
from .brain.reasoner import answer
from .utils.vis import draw_detections
from .models.vlm_qwen import VLM
from .models.face_gender import FaceGender

APP_TITLE = "OmniVision v0.3 — GUI (YOLO + OCR + FaceGender + VLM)"
PREVIEW_MAX_W = 820
PREVIEW_MAX_H = 520

def _resize_to_fit(img: Image.Image, max_w: int, max_h: int) -> Image.Image:
    w, h = img.size
    scale = min(max_w / max(1, w), max_h / max(1, h))
    if scale < 1.0:
        new_size = (max(1, int(w * scale)), max(1, int(h * scale)))
        return img.resize(new_size, Image.LANCZOS)
    return img

def _people_count(dets):
    return sum(1 for d in dets if d.get("label","").lower() == "person")

def _parse_gender_question(q: str) -> str | None:
    s = q.lower()
    male = {"man","men","male","boy","boys","gentleman","gentlemen"}
    female = {"woman","women","female","girl","girls","lady","ladies"}
    if any(w in s for w in male): return "male"
    if any(w in s for w in female): return "female"
    return None

class OmniGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(APP_TITLE)
        self.geometry("1000x700")
        self.minsize(900, 650)

        self.image_path: Path | None = None
        self.annotated_path: Path | None = None
        self.preview_imgtk = None

        try:
            default_device = "cuda" if torch.cuda.is_available() else "cpu"
        except Exception:
            default_device = "cpu"

        self.device_var = tk.StringVar(value=default_device)
        self.status_var = tk.StringVar(value="Ready.")
        self.answer_var = tk.StringVar(value="Answer will appear here.")
        self.ai_mode = tk.BooleanVar(value=True)  # VLM on by default

        self._build_ui()

  
        self.detector = None
        self.ocr = None
        self.vlm = None
        self.face = None
        threading.Thread(target=self._load_models, daemon=True).start()

    def _build_ui(self):
        top = ttk.Frame(self, padding=10)
        top.pack(side=tk.TOP, fill=tk.X)

        ttk.Label(top, text="Device:").pack(side=tk.LEFT)
        dev_box = ttk.Combobox(
            top, width=8, textvariable=self.device_var,
            values=["cuda", "cpu"], state="readonly"
        )
        dev_box.pack(side=tk.LEFT, padx=(4, 12))

        ttk.Button(top, text="Choose Image", command=self._choose_image).pack(side=tk.LEFT)

        ttk.Label(top, text="Question:").pack(side=tk.LEFT, padx=(12, 4))
        self.q_entry = ttk.Entry(top, width=50)
        self.q_entry.insert(0, "How many people are there?")
        self.q_entry.pack(side=tk.LEFT, padx=(0, 8))

        self.run_btn = ttk.Button(top, text="Run", command=self._run_clicked)
        self.run_btn.pack(side=tk.LEFT, padx=(4, 8))

        ttk.Checkbutton(top, text="AI (VLM)", variable=self.ai_mode).pack(side=tk.LEFT)

        self.pb = ttk.Progressbar(top, mode="indeterminate", length=160)
        self.pb.pack(side=tk.RIGHT, padx=8)

        mid = ttk.Frame(self, padding=(10, 6))
        mid.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        self.preview = ttk.Label(mid, anchor="center", relief="groove")
        self.preview.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        right = ttk.Frame(mid, padding=(10, 6), width=260)
        right.pack(side=tk.RIGHT, fill=tk.Y)

        ttk.Label(right, text="Answer", font=("Segoe UI", 11, "bold")).pack(anchor="w")
        ttk.Label(right, textvariable=self.answer_var, wraplength=240, justify="left").pack(anchor="w", pady=(2, 10))

        ttk.Label(right, text="Annotated image path", font=("Segoe UI", 10, "bold")).pack(anchor="w")
        self.path_lbl = ttk.Label(right, text="(none yet)", wraplength=240, justify="left", foreground="#444")
        self.path_lbl.pack(anchor="w", pady=(2, 10))

        bottom = ttk.Frame(self, padding=(10, 6))
        bottom.pack(side=tk.BOTTOM, fill=tk.X)
        ttk.Label(bottom, textvariable=self.status_var).pack(side=tk.LEFT)

    def _load_models(self):
        try:
            self._set_status("Loading models...")
            self.detector = Detector(model_name=YOLO_MODEL, conf=YOLO_CONF, device=self.device_var.get())
            self.ocr = OCR(langs=OCR_LANGS)
            self.vlm = VLM(device=self.device_var.get())
            self.face = FaceGender()
            self._set_status("Models loaded.")
        except Exception as e:
            self._set_status("Model load failed.")
            messagebox.showerror("Error", f"Failed to load models:\n{e}")

    def _choose_image(self):
        ftypes = [("Images", "*.jpg;*.jpeg;*.png;*.bmp;*.webp"), ("All files", "*.*")]
        path = filedialog.askopenfilename(title="Select an image", filetypes=ftypes)
        if not path:
            return
        self.image_path = Path(path)
        self._show_preview(self.image_path)
        self.answer_var.set("Answer will appear here.")
        self.path_lbl.config(text=str(self.image_path))
        self._set_status("Image selected.")

    def _show_preview(self, img_path: Path):
        try:
            img = Image.open(img_path)
            img = _resize_to_fit(img, PREVIEW_MAX_W, PREVIEW_MAX_H)
            self.preview_imgtk = ImageTk.PhotoImage(img)
            self.preview.config(image=self.preview_imgtk)
        except Exception as e:
            messagebox.showerror("Error", f"Could not load image:\n{e}")

    def _run_clicked(self):
        if any(x is None for x in [self.detector, self.ocr, self.vlm, self.face]):
            messagebox.showinfo("Please wait", "Models are still loading...")
            return
        if not self.image_path:
            messagebox.showinfo("Select image", "Please choose an image first.")
            return
        q = self.q_entry.get().strip()
        if not q:
            messagebox.showinfo("Question", "Please type a question.")
            return

        self.run_btn.config(state=tk.DISABLED)
        self.pb.start(10)
        threading.Thread(target=self._analyze_image, args=(self.image_path, q, self.device_var.get()), daemon=True).start()

    def _analyze_image(self, img_path: Path, question: str, device: str):
        try:
            self._set_status("Analyzing...")
            detections = self.detector.detect(str(img_path))
            ocr_results = self.ocr.read(str(img_path))
            faces = self.face.analyze(str(img_path))

         
            ql = question.lower()
            gender_q = _parse_gender_question(ql)
            if "how many" in ql and ("people" in ql or "person" in ql or "persons" in ql or "crowd" in ql):
                final_answer = f"I count {_people_count(detections)} people."
            elif "how many" in ql and gender_q is not None:
                m = sum(1 for f in faces if f.get("gender") == "male")
                w = sum(1 for f in faces if f.get("gender") == "female")
                if gender_q == "male":
                    final_answer = f"I count {m} men."
                else:
                    final_answer = f"I count {w} women."
            else:
                
                if self.ai_mode.get() and self.vlm is not None:
                    final_answer = self.vlm.ask(str(img_path), question)
                else:
                    final_answer = answer(question, detections, ocr_results, faces)

            OUTPUTS.mkdir(parents=True, exist_ok=True)
            fname = f"annotated_{int(time.time())}.jpg"
            annotated_path = OUTPUTS / fname
            draw_detections(str(img_path), detections, str(annotated_path))

            self.after(0, self._update_results, final_answer, annotated_path)
            self._set_status("Done.")
        except Exception as e:
            self._set_status("Failed.")
            messagebox.showerror("Error", f"Analysis failed:\n{e}")
        finally:
            self.after(0, self._enable_run)

    def _update_results(self, final_answer: str, annotated_path: Path):
        self.answer_var.set(final_answer)
        self.annotated_path = annotated_path
        self.path_lbl.config(text=str(annotated_path))
        if annotated_path.exists():
            self._show_preview(annotated_path)

    def _enable_run(self):
        self.run_btn.config(state=tk.NORMAL)
        self.pb.stop()

    def _set_status(self, msg: str):
        self.status_var.set(msg)

def main():
    app = OmniGUI()
    app.mainloop()

if __name__ == "__main__":
    main()


