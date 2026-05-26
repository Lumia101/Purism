from lingua import Language, LanguageDetectorBuilder
from filters.base_filter import BaseFilter

class LanguageFilter(BaseFilter):
    def __init__(self, threshold=0.5):
        self.judge = LanguageDetectorBuilder.from_languages(Language.KOREAN).build()
        self.threshold = threshold

    def apply(self, text: str):
        ratio = self.judge.compute_language_confidence(text, Language.KOREAN)

        if ratio < self.threshold:
            return False
        else:
            return True
