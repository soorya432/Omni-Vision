from typing import Optional
from pathlib import Path
import torch
from PIL import Image
from transformers import AutoProcessor, AutoModelForImageTextToText

MODEL_ID = "Qwen/Qwen2-VL-2B-Instruct"

class VLM:
    def __init__(self, device: Optional[str] = None):
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")
        dtype = torch.float16 if (self.device == "cuda") else torch.float32

        self.processor = AutoProcessor.from_pretrained(
            MODEL_ID, trust_remote_code=True
        )
        self.model = AutoModelForImageTextToText.from_pretrained(
            MODEL_ID, torch_dtype=dtype, device_map="auto", trust_remote_code=True
        )

    @torch.inference_mode()
    def ask(self, image_path: str | Path, question: str, max_new_tokens: int = 128) -> str:
        image = Image.open(image_path).convert("RGB")

        messages = [
            {
                "role": "user",
                "content": [
                    {"type": "image", "image": image},
                    {"type": "text", "text": question},
                ],
            }
        ]

        text = self.processor.apply_chat_template(
            messages, tokenize=False, add_generation_prompt=True
        )

        inputs = self.processor(text=[text], images=[image], return_tensors="pt")
        inputs = {k: v.to(self.model.device) for k, v in inputs.items()}

        output_ids = self.model.generate(
            **inputs, max_new_tokens=max_new_tokens, do_sample=False
        )
        out = self.processor.batch_decode(output_ids, skip_special_tokens=True)[0].strip()

        return out
