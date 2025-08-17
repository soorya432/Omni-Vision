from ultralytics import YOLO

class Detector:
    def __init__(self, model_name="yolov8n.pt", conf=0.25, device=None):
        self.model = YOLO(model_name)
        self.conf = conf
        self.device = device 

    def detect(self, image_path: str):
        res = self.model.predict(source=image_path, conf=self.conf, device=self.device, verbose=False)
        r = res[0]
        items = []
        if getattr(r, "boxes", None) is not None and len(r.boxes) > 0:
            xyxy = r.boxes.xyxy.cpu().numpy().tolist()
            confs = r.boxes.conf.cpu().numpy().tolist()
            clss = r.boxes.cls.cpu().numpy().astype(int).tolist()
            labels = [r.names[c] for c in clss]
            for b, s, cid, lab in zip(xyxy, confs, clss, labels):
                items.append({
                    "bbox": [float(v) for v in b],
                    "score": float(s),
                    "class_id": int(cid),
                    "label": str(lab)
                })
        return items
