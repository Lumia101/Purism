import re
from filters.base_filter import BaseFilter

class LengthFilter(BaseFilter):
    def __init__(self, min_len=50, max_len=10000):
        self.min_len = min_len
        self.max_len = max_len

    def apply(self, text: str):
        actual_len = len(text.strip())
        if self.min_len <= actual_len <= self.max_len:
            return True
        return False

class HarmfulWordsFilter(BaseFilter):
    def __init__(self, filepath="harmful_words.txt", threshold=4):
        self.filepath = filepath
        self.pattern = self._load_and_compile()
        self.threshold = threshold

    def _load_and_compile(self):
        with open(self.filepath, 'r', encoding='utf-8') as f:
            words = sorted(list(set(line.strip() for line in f if line.strip())), key=len, reverse=True)

        if not words:
            raise ValueError(f"It seems {self.filepath} is empty file.")

        combined_pattern = '|'.join(map(re.escape, words))
        return re.compile(combined_pattern)

    def apply(self, text: str):
        if not self.pattern:
            return False

        count = 0
        for _ in self.pattern.finditer(text):
            count += 1
            if count >= self.threshold:
                return False
        return True

class SpamWordsFilter(BaseFilter):
    def __init__(self, filepath="spam_words.txt", threshold=8):
        self.filepath = filepath
        self.pattern = self.load_and_compile()
        self.threshold = threshold

    def load_and_compile(self):
        with open(self.filepath, 'r', encoding='utf-8') as f:
            words = sorted(list(set(line.strip() for line in f if line.strip())), key=len, reverse=True)

        if not words:
            raise ValueError(f"It seems {self.filepath} is empty file.")

        combined_pattern = '|'.join(map(re.escape, words))
        return re.compile(combined_pattern)

    def apply(self, text: str):
        if not self.pattern:
            return False

        # 효율적인 처리를 위해 3개까지만 찾고 중단
        count = 0
        for _ in self.pattern.finditer(text):
            count += 1
            if count >= self.threshold:
                return False
        return True

class SignAbuseFilter(BaseFilter):
    def __init__(self, threshold=0.3):
        self.threshold = threshold
        self.signabuse = re.compile(r'[^a-zA-Z0-9가-힣\s]')

    def apply(self, text: str):
        len_all = len(text)
        len_sign = len(self.signabuse.findall(text))

        if len_all == 0:
            return False
        if len_sign / len_all >= self.threshold:
            return False
        return True

class PIIFilter(BaseFilter):
    def __init__(self):
        # 주요 개인정보 패턴들을 사전 형태로 정리
        self.pii_patterns = {
            "resident_number": re.compile(r'\d{2}([01]\d[0123]\d)-?[1-4]\d{6}'),
            "phone_number": re.compile(r'01[016789]-?\d{3,4}-?\d{4}'),
            "email": re.compile(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'),
            "card_number": re.compile(r'(?:\d{4}[- ]?){3}\d{4}')
        }

    def apply(self, text: str):
        for name, pattern in self.pii_patterns.items():
            if pattern.search(text):
                return False
        return True
