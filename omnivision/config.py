from pathlib import Path

YOLO_MODEL = "yolov8n.pt"   
YOLO_CONF = 0.25            


ROOT = Path(__file__).resolve().parent
OUTPUTS = ROOT / "outputs"
(OUTPUTS / "..").resolve()  

PROJECT_ROOT = ROOT.parent
(PROJECT_ROOT / "outputs").mkdir(parents=True, exist_ok=True)


OCR_LANGS = ["en"]
