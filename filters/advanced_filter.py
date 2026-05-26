from lingua import Language, LanguageDetectorBuilder
from filters.base_filter import BaseFilter

class LanguageFilter(BaseFilter):
    def __init__(self):
        self.judge = LanguageDetectorBuilder.from_languages(Language.KOREAN).build()

    def apply(self, text: str):
        match = self.judge.detect_language_of(text)

        if match == Language.KOREAN:
            return True
        else:
            return False
