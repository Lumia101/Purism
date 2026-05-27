# Load libraries
import re
from .base_filter import BaseFilter
from importlib.resources import files

# If the length is too long or too short, remove it
class LengthFilter(BaseFilter):
    def __init__(self, min_len=50, max_len=10000):
        self.min_len = min_len
        self.max_len = max_len

    def apply(self, text: str):
        actual_len = len(text.strip()) # Remove the blank
        if self.min_len <= actual_len <= self.max_len:
            return True
        return False

# Remove any inappropriate words
# You can customize settings by editing the .txt file.
class HarmfulWordsFilter(BaseFilter):
    def __init__(self, threshold=4):
        self.filepath = files("dataprism.resources").joinpath(
            "harmful_words.txt"
        )
        self.pattern = self.load_and_compile()
        self.threshold = threshold

    def load_and_compile(self):
        # Open .txt file which contains harmful words
        with open(self.filepath, 'r', encoding='utf-8') as f:
            words = sorted(list(set(line.strip() for line in f if line.strip())), key=len, reverse=True)
            
        # If the file is empty, stop running.
        if not words:
            raise ValueError("It seems the list of forbidden words is empty.")

        combined_pattern = '|'.join(map(re.escape, words))
        return re.compile(combined_pattern)

    def apply(self, text: str):
        if not self.pattern:
            return False

        # Detects and stops only a set number of times for speed
        count = 0
        for _ in self.pattern.finditer(text):
            count += 1
            if count >= self.threshold:
                return False
        return True

# It is virtually identical to HarmfulWordsFilter.
# However, it is used to prevent errors and accidental mistakes.
class SpamWordsFilter(BaseFilter):
    def __init__(self, threshold=8):
        self.filepath = files("dataprism.resources").joinpath(
            "spam_words.txt"
        )
        self.pattern = self.load_and_compile()
        self.threshold = threshold

    def load_and_compile(self):
        with open(self.filepath, 'r', encoding='utf-8') as f:
            words = sorted(list(set(line.strip() for line in f if line.strip())), key=len, reverse=True)

        if not words:
            raise ValueError("It seems the list of forbidden words is empty.")

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

# If text have used too many symbols, remove it
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

# If personal information is included, remove it
class PIIFilter(BaseFilter):
    def __init__(self):
        # Compiling key forms of personal information
        self.pii_patterns = {
            "resident_number": re.compile(r'\d{2}([01]\d[0123]\d)-?[1-4]\d{6}'),
            "phone_number": re.compile(r'01[016789]-?\d{3,4}-?\d{4}'),
            "email": re.compile(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'),
            "card_number": re.compile(r'(?:\d{4}[- ]?){3}\d{4}')
        }

    def apply(self, text: str):
        # Return False immediately if any personal information is found
        for name, pattern in self.pii_patterns.items():
            if pattern.search(text):
                return False
        return True
