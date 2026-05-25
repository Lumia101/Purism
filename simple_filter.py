import re
from DataPrism.base_filter import BaseFilter

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
    def __init__(self, filepath="harmful_words.txt"):
        self.filepath = filepath
        self.pattern = self._load_and_compile()

    def _load_and_compile(self):
        try:
            with open(self.filepath, 'r', encoding='utf-8') as f:
                words = sorted(list(set(line.strip() for line in f if line.strip())), key=len, reverse=True)
            
            if not words:
                return None
            
            combined_pattern = '|'.join(map(re.escape, words))
            return re.compile(combined_pattern)

        except FileNotFoundError:
            print(f"{self.filepath} is invalid file.")
            return None

    def filter(self, text: str) -> bool:
        if not self.pattern:
            return True
        
        # 효율적인 처리를 위해 3개까지만 찾고 중단
        count = 0
        for _ in self.pattern.finditer(text):
            count += 1
            if count >= 3:
                return False
        return True

if __name__ == "__main__":
    filtering1 = HarmfulWordsFilter()
    filtering2 = LengthFilter(10, 100000)
    test = [
        "전라디언 새끼가 어디 와서 까부냐 ㅅㅂ럼아 느금마 개새끼",
        "한국에는 저런 이상한 극우 사칭들이 너무 많아요",
        "오늘 날씨는 맑습니다.",
        "ㅅㅂ ㅅㅂㅅㅂㅂ ㅅㅂ ㅅㅂㅅㅂ",
        "요즘 인공지능 많이 발전했네.",
        "아"
    ]

    for i in range(0, 6):
        if filtering1.filter(test[i]) and filtering2.filter(test[i]):
            print("검열 안 됨")
        else:
            print("검열됨")
