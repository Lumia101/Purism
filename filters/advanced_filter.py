from lingua import Language, LanguageDetectorBuilder
from filters.base_filter import BaseFilter

class LanguageFilter(BaseFilter):
    def __init__(self, threshold=0.6, fast_drop=10):
        self.judge = LanguageDetectorBuilder.from_languages(
            Language.KOREAN,
            Language.JAPANESE,
            Language.CHINESE, 
            Language.ENGLISH
        ).build()
        self.threshold = threshold
        self.fastdrop = fast_drop

    def apply(self, text: str):
        if len(text.strip()) < self.fastdrop:
            return False
        
        match = self.judge.compute_language_confidence(text, Language.KOREAN)

        if match is None:
            return False
        
        if match >= self.threshold:
            return True
        else:
            return False
