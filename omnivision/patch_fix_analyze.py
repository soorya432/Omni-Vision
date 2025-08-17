from pathlib import Path
import re

p = Path("omnivision/gui.py")
src = p.read_text(encoding="utf-8", errors="ignore")

new_func = r"""
    def _analyze_image(self, img_path: Path, question: str, device: str):
        try:
            self._set_status("Analyzing...")
            detections = self.detector.detect(str(img_path))
            ocr_results = self.ocr.read(str(img_path))

   
            final_answer = self.vlm.ask(str(img_path), question)

            OUTPUTS.mkdir(parents=True, exist_ok=True)
            fname = f"annotated_{int(time.time())}.jpg"
            annotated_path = OUTPUTS / fname
            draw_detections(str(img_path), detections, str(annotated_path))

            self.after(0, self._update_results, final_answer, annotated_path)
            self._set_status("Done.")
        except Exception as e:
            self._set_status("Failed.")
            messagebox.showerror("Error", f"Analysis failed:\\n{e}")
        finally:
            self.after(0, self._enable_run)
"""


start = src.find("def _analyze_image(")
if start == -1:
    raise SystemExit("Could not find def _analyze_image(...) in gui.py")

tail = src[start:]
m = re.search(r"\n(?=def\s|\nclass\s|if __name__ ==)", tail, flags=re.S)
if m:
    end = start + m.start()
else:
    end = len(src)

patched = src[:start] + new_func + src[end:]
p.write_text(patched, encoding="utf-8")
print("✅ Replaced _analyze_image() with VLM-only version.")
