from normalizers.normalizer import Normalizer
from filters.base_filter import BaseFilter
from filters.simple_filter import LengthFilter, HarmfulWordsFilter, SpamWordsFilter, SignAbuseFilter, PIIFilter

class PurifyConfig():
    def __init__(self, filters):
        self.normalizer = Normalizer()
        self.filters = filters

    def purify(self, text: str):
        text_cleaned = self.normalizer.normalize(text)

        for filter in self.filters:
            if not filter.apply(text_cleaned):
                return {
                    "raw_text": text,
                    "passed": False,
                    "filtered_by": filter.__class__.__name__,
                    "normalized_text": text_cleaned
                }

        return {
            "raw_text": text,
            "passed": True,
            "filtered_by": None,
            "normalized_text": text_cleaned
        }
