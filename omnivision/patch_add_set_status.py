from pathlib import Path
import re

p = Path("omnivision/gui.py")
s = p.read_text(encoding="utf-8", errors="ignore")

if "def _set_status(self, msg:" not in s:

    cls_start = s.find("class OmniGUI(")
    if cls_start == -1:
        raise SystemExit("Could not find class OmniGUI in gui.py")

    tail = s[cls_start:]
    m = re.search(r"\n(?=def\s+main\s*\(|class\s+|\Z)", tail, flags=re.S)
    insert_at = (cls_start + m.start()) if m else len(s)

    patch = """
    def _set_status(self, msg: str):
        # safe in main thread; background threads call via self.after(...)
        self.status_var.set(msg)
"""

    s = s[:insert_at] + patch + s[insert_at:]
    p.write_text(s, encoding="utf-8")
    print("✅ Inserted _set_status() into OmniGUI.")
else:
    print("ℹ️ _set_status() already present; no change.")
