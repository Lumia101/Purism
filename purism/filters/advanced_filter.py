# Load libraries
import hashlib

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
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
                Language.FRENCH,
            ).build()

    def apply(self, text: str):
        self.load_judge()
        match = self.judge.compute_language_confidence(text, Language.KOREAN)

        if match is None:
            return False

        return match >= self.threshold


# Remove duplicate content
class DedupFilter(BaseFilter):
    def __init__(self, threshold=0.7, num_perm=128, shingles=3):
        self.threshold = threshold
        self.num_perm = num_perm
        self.shingle = shingles
        self.lsh = MinHashLSH(
            threshold=self.threshold,
            num_perm=self.num_perm,
        )

        self.exact_hashes = set()
        self.count = 0

    def get_minhash(self, text):
        m = MinHash(num_perm=self.num_perm)
        if len(text) < self.shingle:
            m.update(text.encode("utf8"))
            return m

        for i in range(len(text) - self.shingle + 1):
            token = text[i : i + self.shingle]
            m.update(token.encode("utf8"))

        return m

    def apply(self, text: str):
        text = text.strip()
        if not text:
            return False

        # Exact Dedup
        exact_hash = hashlib.sha256(text.encode("utf8")).hexdigest()
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
    def __init__(self, ppl_threshold=400.0, batch_size=16):
        self.model_id = "LiquidAI/LFM2.5-350M"
        self.model = None
        self.tokenizer = None
        self.ppl_threshold = ppl_threshold
        self.precision = torch.bfloat16 if torch.cuda.is_bf16_supported(including_emulation=False) else torch.float16
        self.batch_size = batch_size

    def load_model(self):
        if self.model is None:
            self.model = AutoModelForCausalLM.from_pretrained(
                self.model_id,
                device_map="auto",
                torch_dtype="auto"
            )
            self.model.eval()

        if self.tokenizer is None:
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_id)
            if self.tokenizer.pad_token is None:
                self.tokenizer.pad_token = self.tokenizer.eos_token

    def compute_ppl_batch(self, texts: list[str]):
        if not texts:
            return []

        device = next(self.model.parameters()).device
        enc = self.tokenizer(
            texts,
            return_tensors="pt",
            padding=True,
            truncation=True,
            max_length=512,
        ).to(device)

        input_ids = enc["input_ids"]
        attention_mask = enc["attention_mask"]

        with torch.no_grad():
            outputs = self.model(
                input_ids=input_ids,
                attention_mask=attention_mask,
            )
            logits = outputs.logits

            shift_logits = logits[:, :-1, :].contiguous()
            shift_labels = input_ids[:, 1:].contiguous()
            shift_mask = attention_mask[:, 1:].contiguous()

            loss_fct = torch.nn.CrossEntropyLoss(reduction="none")
            loss = loss_fct(
                shift_logits.reshape(-1, shift_logits.size(-1)),
                shift_labels.reshape(-1),
            )
            loss = loss.view(shift_labels.size())

            denom = shift_mask.sum(dim=1).clamp_min(1)
            sentence_loss = (loss * shift_mask).sum(dim=1) / denom

        return torch.exp(sentence_loss).cpu().tolist()

    def apply_batch(self, texts: list[str]):
        self.load_model()

        results = [False] * len(texts)
        valid_texts = []
        valid_indices = []

        for i, t in enumerate(texts):
            if not isinstance(t, str):
                continue

            clean_t = t.strip()
            if len(clean_t) < 10:
                continue

            valid_texts.append(clean_t)
            valid_indices.append(i)

        if not valid_texts:
            return results

        all_ppls = []
        for i in range(0, len(valid_texts), self.batch_size):
            batch_chunk = valid_texts[i : i + self.batch_size]
            all_ppls.extend(self.compute_ppl_batch(batch_chunk))

        for idx, ppl in zip(valid_indices, all_ppls):
            results[idx] = ppl <= self.ppl_threshold

        return results

    def apply(self, text: list[str]):
        return self.apply_batch([text])[0]
