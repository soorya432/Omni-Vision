import cv2
from typing import List, Dict

def draw_detections(image_path: str, detections: List[Dict], out_path: str):
    img = cv2.imread(image_path)
    if img is None:
        return None
    for det in detections:
        x1, y1, x2, y2 = map(int, det["bbox"])
        label = f'{det["label"]} {det["score"]:.2f}'
        cv2.rectangle(img, (x1,y1), (x2,y2), (0,255,0), 2)
        cv2.putText(img, label, (x1, max(y1-5, 0)), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,255,0), 1, cv2.LINE_AA)
    cv2.imwrite(out_path, img)
    return out_path
