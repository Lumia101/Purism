# Load libraries
import hashlib
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
from lingua import Language, LanguageDetectorBuilder
from datasketch import MinHash, MinHashLSH
from .base_filter import BaseFilter

# Use the lingua library to remove non-Korean sentences
class LanguageFilter(BaseFilter):
    def __init__(self, threshold=0.6):
        self.judge = None
        self.threshold = threshold

    def load_judge(self):
        if self.judge is None:
            self.judge = LanguageDetectorBuilder.from_languages(
                Language.KOREAN,
                Language.JAPANESE,
                Language.CHINESE, 
                Language.ENGLISH,
                Language.FRENCH
            ).build()

    def apply(self, text: str):
        self.load_judge()
        match = self.judge.compute_language_confidence(text, Language.KOREAN)

        if match is None:
            return False
        
        if match >= self.threshold:
            return True
        else:
            return False

# Remove duplicate content
class DedupFilter(BaseFilter):
    def __init__(self, threshold=0.7, num_perm=128, shingles=3):
        self.threshold = threshold
        self.num_perm = num_perm
        self.shingle = shingles
        self.lsh = MinHashLSH(
            threshold=self.threshold,
            num_perm=self.num_perm
        )

        self.exact_hashes = set()
        self.count = 0

    def get_minhash(self, text):
        m = MinHash(num_perm=self.num_perm)
        if len(text) < self.shingle:
            m.update(text.encode('utf8'))
            return m

        for i in range(len(text) - self.shingle + 1):
            token = text[i:i+self.shingle]
            m.update(token.encode("utf8"))

        return m

    def apply(self, text: str):
        # Remove a sentence with nothing
        text = text.strip()
        if not text:
            return False

        # Exact Dedup
        exact_hash = hashlib.sha256(
            text.encode("utf8")
        ).hexdigest()

        if exact_hash in self.exact_hashes:
            return False

        self.exact_hashes.add(exact_hash)

        # Near Dedup
        m = self.get_minhash(text)
        result = self.lsh.query(m)

        if result:
            return False

        self.count += 1
        self.lsh.insert(str(self.count), m)
        return True

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
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_id)

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