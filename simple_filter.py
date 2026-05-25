import re
from DataPrism.base_filter import BaseFilter

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
    def __init__(self, filepath="harmful_words.txt"):
        self.filepath = filepath
        self.pattern = self._load_and_compile()

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
        
        # 효율적인 처리를 위해 3개까지만 찾고 중단
        count = 0
        for _ in self.pattern.finditer(text):
            count += 1
            if count >= 3:
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

if __name__ == "__main__":
    filters = [
        HarmfulWordsFilter(),
        LengthFilter(10, 10000),
        SignAbuseFilter(0.2)
    ]

    test = [
        "전라디언 새끼가 어디 와서 까부냐 ㅅㅂ럼아 느금마 개새끼",
        "한국에는 저런 이상한 극우 사칭들이 너무 많아요",
        "================== 공지 =====================",
        "ㅅㅂ ㅅㅂㅅㅂㅂ ㅅㅂ ㅅㅂㅅㅂ",
        "요즘 인공지능 많이 발전했네.",
        "아",
        "광양출장맛사지➵예약♡대구 모텔 추천（카톡hwp63）♠﹛мss798.сом﹜━광양오피스 걸♚광양콜걸만남γ광양대구 여관►광양서울 조건 만남↲광양군산 여관"
        "2024년 12월 3일에 무슨 일이 일어났는지 기억하자."
    ]

    for i, value in enumerate(test):
        passed = all(f.apply(test[i]) for f in filters)

        if passed:
            print("통과")
        else:
            print("검열됨")
