from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
from filters.base_filter import BaseFilter

ppl_model_id = "LiquidAI/LFM2.5-1.2B-Instruct"

class PPLFilter(BaseFilter):
    def __init__(self, drop_cut=100.0):
        self.quant_config = BitsAndBytesConfig(load_in_8bit=True)
        self.ppl_model = AutoModelForCausalLM.from_pretrained(
            "LiquidAI/LFM2.5-1.2B-Instruct",
            device_map="auto",
            dtype="auto",
            quantization_config=quant_config
        )
        self.tokenizer = AutoTokenizer.from_pretrained("LiquidAI/LFM2.5-1.2B-Instruct")
        self.drop_ratio = drop_ratio
        
     def
