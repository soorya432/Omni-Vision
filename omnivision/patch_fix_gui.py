from pathlib import Path
import re

p = Path("omnivision/gui.py")
s = p.read_text(errors="ignore")


s = (s.replace("�", "-")
     .replace("\u2013", "-").replace("\u2014", "-")   # en/em dashes
     .replace("\u2018", "'").replace("\u2019", "'")   # curly single quotes
     .replace("\u201C", '"').replace("\u201D", '"'))  # curly double quotes


s = re.sub(r'self\.ai_mode\s*=\s*tk\.BooleanVar\(value=\s*False\s*\)',
           'self.ai_mode = tk.BooleanVar(value=True)', s)


s = re.sub(
    r'# SMART:.*?draw_detections',
    (
        'final_answer = self.vlm.ask(str(img_path), question)\n\n'
        '            OUTPUTS.mkdir(parents=True, exist_ok=True)\n'
        '            fname = f"annotated_{int(time.time())}.jpg"\n'
        '            annotated_path = OUTPUTS / fname\n'
        '            draw_detections'
    ),
    s,
    flags=re.S
)

p.write_text(s, encoding="utf-8")
print("✅ Patched omnivision/gui.py: unicode fixed + VLM-only enabled")
