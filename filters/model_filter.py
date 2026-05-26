import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
from filters.base_filter import BaseFilter

ppl_model_id = "LiquidAI/LFM2.5-1.2B-Instruct"

class PPLFilter(BaseFilter):
    def __init__(self, drop_ratio=180.0):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.quant_config = BitsAndBytesConfig(load_in_8bit=True)
        self.model = AutoModelForCausalLM.from_pretrained(
            "LiquidAI/LFM2.5-1.2B-Instruct",
            device_map=self.device,
            dtype="auto",
            quantization_config=quant_config
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
        ).to(self.device)
        
        with torch.no_grad():
            output = self.model(**enc, labels=enc["input_ids"])
            loss = output.loss

        return torch.exp(loss).item()
        
    def apply(self, text: str):
        if not text.strip():
            return False

        ppl = self.compute_ppl(text)
        return ppl <= self.drop_ratio
