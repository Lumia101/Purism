# Load libraries
import hashlib
from lingua import Language, LanguageDetectorBuilder
from datasketch import MinHash, MinHashLSH
from filters.base_filter import BaseFilter

# Use the lingua library to remove non-Korean sentences
class LanguageFilter(BaseFilter):
    def __init__(self, threshold=0.6):
        self.judge = LanguageDetectorBuilder.from_languages(
            Language.KOREAN,
            Language.JAPANESE,
            Language.CHINESE, 
            Language.ENGLISH
        ).build()
        self.threshold = threshold

    def apply(self, text: str):
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
