import easyocr

class OCR:
    def __init__(self, langs=None):
        self.reader = easyocr.Reader(langs or ["en"], gpu=True)

    def read(self, image_path: str):
        raw = self.reader.readtext(image_path, detail=1, paragraph=False)
        out = []
        for bbox, text, conf in raw:
            out.append({
                "bbox": [[float(x), float(y)] for (x, y) in bbox],
                "text": str(text),
                "score": float(conf)
            })
        return out
