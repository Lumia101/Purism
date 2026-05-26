from lingua import Language, LanguageDetectorBuilder
from filters.base_filter import BaseFilter

class LanguageFilter(BaseFilter):
    def __init__(self):
        self.judge = LanguageDetectorBuilder.from_all_languages().build()

    def apply(self, text: str):
        match = self.judge.detect_language_of(text)

        if match.iso_code_639_1.name == "KO":
            return True
        else:
            return False
