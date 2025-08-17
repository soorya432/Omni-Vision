from pathlib import Path
import re

p = Path("omnivision/gui.py")
src = p.read_text(encoding="utf-8", errors="ignore")

def ensure_method(src: str, method_name: str, body: str) -> str:
    if f"def {method_name}(" in src:
        return src  # already present
    # Insert near the end of class OmniGUI (before next top-level def/class)
    cls_pos = src.find("class OmniGUI(")
    if cls_pos == -1:
        raise SystemExit("Could not find class OmniGUI in gui.py")
    tail = src[cls_pos:]
    m = re.search(r"\n(?=def\s+main\s*\(|class\s+|\Z)", tail, flags=re.S)
    insert_at = (cls_pos + m.start()) if m else len(src)
    return src[:insert_at] + body + src[insert_at:]

# Define minimal implementations
set_status_body = """
    def _set_status(self, msg: str):
        # Safe to call on main thread; background threads should use self.after(...)
        self.status_var.set(msg)
"""

enable_run_body = """
    def _enable_run(self):
        try:
            self.run_btn.config(state=tk.NORMAL)
        except Exception:
            pass
        try:
            self.pb.stop()
        except Exception:
            pass
"""

update_results_body = """
    def _update_results(self, final_answer, annotated_path):
        # Update right panel and preview with annotated image
        try:
            self.answer_var.set(str(final_answer))
        except Exception:
            pass
        try:
            from pathlib import Path as _Path
            self.annotated_path = _Path(annotated_path)
            self.path_lbl.config(text=str(self.annotated_path))
        except Exception:
            pass
        try:
            if self.annotated_path and self.annotated_path.exists():
                from PIL import Image, ImageTk
                img = Image.open(self.annotated_path)
                img = _resize_to_fit(img, PREVIEW_MAX_W, PREVIEW_MAX_H)
                self.preview_imgtk = ImageTk.PhotoImage(img)
                self.preview.config(image=self.preview_imgtk)
        except Exception:
            pass
"""


src = ensure_method(src, "_set_status", set_status_body)
src = ensure_method(src, "_enable_run", enable_run_body)
src = ensure_method(src, "_update_results", update_results_body)

p.write_text(src, encoding="utf-8")
print("✅ Helpers ensured: _set_status, _enable_run, _update_results")
