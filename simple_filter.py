from .base_filter import BaseFilter
import re

class LengthFilter(BaseFilter):
    def __init__(self, min_len=50, max_len=10000):
        self.min_len = min_len
        self.max_len = max_len

    def filter(self, text: str):
        actual_len = len(text.strip())
        if self.min_len <= actual_len <= self.max_len:
            return True
        return False

class HarmfulWordsFilter(BaseFilter):
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.pattern = self.load_and_compile()

    def load_and_compile(self):
        with open(self.file_path, 'r', encoding='utf-8') as f:
            words = [line.strip() for line in f if line.strip()]
        combined_pattern = '|'.join(map(re.escape, words))
        return re.compile(combined_pattern)
        
    def filter():
        if self.pattern.search(text):
            return False
        return True