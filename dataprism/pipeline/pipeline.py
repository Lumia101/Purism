# Import all created Python codes from this repository
from dataprism.normalizers.normalizer import TextCleaner, UICleaner, UnicodeCleaner
from dataprism.filters.simple_filter import LengthFilter, HarmfulWordsFilter, SpamWordsFilter, SignAbuseFilter, PIIFilter
from dataprism.filters.advanced_filter import LanguageFilter
from dataprism.filters.model_filter import PPLFilter

# Setting Settings for Data Purification
class PurifyConfig():
    def __init__(self, filters, normalizer):
        self.normalizer = normalizer
        self.filters = filters

    def purify(self, text: str):
        for normalizer in self.normalizer:
            text_cleaned = normalizer.normalize(text)

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
