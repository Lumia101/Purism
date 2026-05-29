# Import all created Python codes from this repository
from joblib import Parallel, delayed
from purism.normalizers.normalizer import TextCleaner, UICleaner, UnicodeCleaner
from purism.filters.simple_filter import LengthFilter, HarmfulWordsFilter, SpamWordsFilter, SignAbuseFilter, PIIFilter
from purism.filters.advanced_filter import LanguageFilter, DedupFilter
from purism.filters.model_filter import PPLFilter

# Setting Settings for Data Purification
class PurifyConfig():
    def __init__(self, normalizer, filter_cpu, filter_gpu):
        self.normalizer = normalizer
        self.filter_cpu = filter_cpu
        self.filter_gpu = filter_gpu
    
    def fast_purify(self, text: str):
        text_cleaned = text
        for normalizer in self.normalizer:
            text_cleaned = normalizer.normalize(text_cleaned)
        
        for flt in self.filter_cpu:
            if not flt.apply(text_cleaned):
                return {
                    "passed": False,
                    "filtered_by": flt.__class__.__name__,
                    "text": text_cleaned
                }

        return {
            "passed": True,
            "filtered_by": None,
            "text": text_cleaned
        }

    def heavy_purify(self, text: str):
        for flt in self.filter_gpu:
            if not flt.apply(text):
                return {
                    "passed": False,
                    "filtered_by": flt.__class__.__name__,
                    "text": text
                }

        return {
            "passed": True,
            "filtered_by": None,
            "text": text
        }

    def parallel_purify(self, texts: list, n_process=-1):
        final_results = []
        parallel = Parallel(n_jobs=n_process)
        fast_results = parallel(
            delayed(self.fast_purify)(text) for text in texts
        )

        for text in fast_results:
            if text["passed"]:
                final_results.append(self.heavy_purify(text["text"]))
            else:
                final_results.append(text)
    
        return final_results
