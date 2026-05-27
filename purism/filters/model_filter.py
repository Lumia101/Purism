import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
from .base_filter import BaseFilter

class PPLFilter(BaseFilter):
    def __init__(self, ppl_threshold=180.0):
        model_id = "LiquidAI/LFM2.5-1.2B-Instruct"
        self.quant_config = BitsAndBytesConfig(load_in_8bit=True)
        self.model = AutoModelForCausalLM.from_pretrained(
            model_id,
            device_map="auto",
            dtype="auto",
            quantization_config=self.quant_config
        )
        self.model.eval()
        
        self.tokenizer = AutoTokenizer.from_pretrained(model_id)
        self.drop_ratio = ppl_threshold

    def compute_ppl(self, text: str):
        device = next(
            self.model.parameters()
        ).device
        enc = self.tokenizer(
            text,
            return_tensors="pt",
            truncation=True,
            max_length=512
        ).to(device)
        
        with torch.no_grad():
            output = self.model(
                **enc,
                labels=enc["input_ids"]
            )
            loss = output.loss

        ppl = torch.exp(loss)
        
        if torch.isinf(ppl):
            return float("inf")
            
        return ppl.item()
        
    def apply(self, text: str):
        text = text.strip()
        if len(text) < 10:
            return False

        ppl = self.compute_ppl(text)
        return ppl <= self.drop_ratio
