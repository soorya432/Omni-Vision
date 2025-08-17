
from __future__ import annotations
import re
from collections import Counter
from typing import List, Dict, Optional

def _norm(s: str) -> str:
    return re.sub(r"\s+", " ", s.strip().lower())

def _is_text_question(question: str) -> bool:
    q = _norm(question)
    keys = ["text", "say", "written", "words", "read", "label"]
    return any(k in q for k in keys)

def _people_count(dets: List[Dict]) -> int:
    return sum(1 for d in dets if d.get("label", "").lower() == "person")

_M_MALE = {"man", "men", "male", "boy", "boys", "gentleman", "gentlemen"}
_M_FEMALE = {"woman", "women", "female", "girl", "girls", "lady", "ladies"}

def _gender_query(question: str) -> Optional[str]:
    q = _norm(question)
    if any(w in q for w in _M_MALE):
        return "male"
    if any(w in q for w in _M_FEMALE):
        return "female"
    return None

def _summary_from_detections(detections: List[Dict]) -> str:
    labels = [d.get("label", "") for d in detections]
    counts = Counter(labels)
    parts = [f"{lab} x{cnt}" for lab, cnt in counts.most_common(5)]
    return ", ".join(parts) if parts else "no objects detected"

def _summary_from_ocr(ocr: List[Dict]) -> str:
    if not ocr:
        return "no legible text detected"
    top = sorted(ocr, key=lambda x: x.get("score", 0.0), reverse=True)[:3]
    texts = [f"\"{o.get('text','')}\"" for o in top if o.get("text")]
    return "; ".join(texts) if texts else "no legible text detected"

def answer(question: str,
           detections: List[Dict],
           ocr: List[Dict],
           faces: Optional[List[Dict]] = None) -> str:
    q = _norm(question)


    if _is_text_question(q):
        return f"I can read: {_summary_from_ocr(ocr)}."

 
    gq = _gender_query(q)
    if gq is not None:
        if not faces:
            return "I couldn't detect clear faces to estimate."
        n = sum(1 for f in faces if f.get("gender") == gq)
        noun = "men" if gq == "male" else "women"
        return f"I count {n} {noun}."

   
    if "how many" in q and ("people" in q or "persons" in q or "person" in q or "crowd" in q):
        return f"I count {_people_count(detections)} people."

    
    scene = _summary_from_detections(detections)
    text = _summary_from_ocr(ocr)
    if text != "no legible text detected":
        return f"I see {scene}. Also text: {text}"
    return f"I see {scene}."
