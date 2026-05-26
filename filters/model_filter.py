import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
from filters.base_filter import BaseFilter

ppl_model_id = "LiquidAI/LFM2.5-1.2B-Instruct"

class PPLFilter(BaseFilter):
    def __init__(self, ppl_threshold=180.0):
        self.quant_config = BitsAndBytesConfig(load_in_8bit=True)
        self.model = AutoModelForCausalLM.from_pretrained(
            "LiquidAI/LFM2.5-1.2B-Instruct",
            device_map="auto",
            dtype="auto",
            quantization_config=self.quant_config
        )
        self.model.eval()
        
        self.tokenizer = AutoTokenizer.from_pretrained("LiquidAI/LFM2.5-1.2B-Instruct")
        self.drop_ratio = drop_ratio

    def compute_ppl(self, text: str):
        enc = self.tokenizer(
            text,
            return_tensors="pt",
            truncation=True,
            max_length=512
        ).to(self.model.device)
        
        with torch.no_grad():
            output = self.model(
                **enc,
                labels=enc["input_ids"]
            )
            loss = output.loss

        return torch.exp(loss).item()
        
    def apply(self, text: str):
        text = text.strip()
        if not text:
            return False

        ppl = self.compute_ppl(text)
        return ppl <= self.drop_ratio
