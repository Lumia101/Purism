import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
from .base_filter import BaseFilter

# Measure the PPL of corpus and filter corpus with excessively high PPL.
class PPLFilter(BaseFilter):
    def __init__(self, ppl_threshold=180.0):
        self.model_id = "LiquidAI/LFM2.5-1.2B-Instruct"
        self.model = None
        self.tokenizer = None
        self.ppl_threshold = ppl_threshold

    def load_model(self):
        if self.model is None:
            quant_config = BitsAndBytesConfig(
                load_in_4bit=True,
                bnb_4bit_quant_type="nf4",
                bnb_4bit_use_double_quant=True
            )
            self.model = AutoModelForCausalLM.from_pretrained(
                self.model_id,
                device_map="auto",
                dtype="auto",
                quantization_config=quant_config
            )
            self.model.eval()

        if self.tokenizer is None:
            self.tokenizer = AutoTokenizer.from_pretrained(model_id)
    
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
        self.load_model()
        if len(text) < 10:
            return False

        ppl = self.compute_ppl(text)
        return ppl <= self.ppl_threshold 
