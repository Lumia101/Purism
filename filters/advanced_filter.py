# Load libraries
from lingua import Language, LanguageDetectorBuilder
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
        self.threshold = threshold # 

    def apply(self, text: str):
        match = self.judge.compute_language_confidence(text, Language.KOREAN)

        if match is None:
            return False
        
        if match >= self.threshold:
            return True
        else:
            return False
