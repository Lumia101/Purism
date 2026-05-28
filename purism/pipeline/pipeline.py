# Import all created Python codes from this repository
import multiprocessing
from concurrent.futures import ProcessPoolExecutor
from typing import List, Dict, Any
from functools import partial
from purism.normalizers.normalizer import TextCleaner, UICleaner, UnicodeCleaner
from purism.filters.simple_filter import LengthFilter, HarmfulWordsFilter, SpamWordsFilter, SignAbuseFilter, PIIFilter
from purism.filters.advanced_filter import LanguageFilter, DedupFilter
from purism.filters.model_filter import PPLFilter

# Setting Settings for Data Purification
class PurifyConfig():
    def __init__(self, filters, normalizer):
        self.normalizer = normalizer
        self.filters = filters

    def purify(self, text: str):
        text_cleaned = text
        for normalizer in self.normalizer:
            text_cleaned = normalizer.normalize(text_cleaned)

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

    def multi_purify(self, texts: str, n_process: int=None, chunk_size=100):
        if n_process is None:
            n_process = multiprocessing.cpu_count()

        with ProcessPoolExecutor(max_workers=n_process) as executor:
            results = list(executor.map(self.purify, texts, chunksize=chunksize))
        
        return results