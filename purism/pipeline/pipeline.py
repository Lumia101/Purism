# Import all created Python codes from this repository
from joblib import Parallel, delayed
from tqdm.auto import tqdm
from purism.normalizers.normalizer import TextCleaner, UICleaner, UnicodeCleaner
from purism.filters.simple_filter import LengthFilter, HarmfulWordsFilter, SpamWordsFilter, SignAbuseFilter, PIIFilter
from purism.filters.advanced_filter import LanguageFilter, DedupFilter, PPLFilter

# Setting Settings for Data Purification
class PurifyConfig():
    def __init__(self, normalizer, filter_multi, filter_normal):
        self.normalizer = normalizer
        self.filter_multi = filter_multi
        self.filter_normal = filter_normal

    def multi_purify(self, text: str):
        text_cleaned = text
        for normalizer in self.normalizer:
            text_cleaned = normalizer.normalize(text_cleaned)
        
        for flt in self.filter_multi:
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

    def normal_purify(self, text: str):
        for flt in self.filter_normal:
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
        n_passed = 0
        n_filtered_multi = 0
        n_filtered_normal = 0
        final_results = []

        fast_results = Parallel(n_jobs=n_process)(
            delayed(self.multi_purify)(text) for text in tqdm(texts, desc="Applying MultiCore filter", unit="texts")
        )

        pbar = tqdm(fast_results, desc="Applying Batch filter", unit="texts")
        
        for text in pbar:
            if text["passed"]:
                text_p = self.normal_purify(text["text"])
                final_results.append(text_p)

                if text_p["passed"]:
                    n_passed += 1
                else:
                    n_filtered_normal += 1
            else:
                final_results.append(text)
                n_filtered_normal += 1

            total = len(texts)
            
            if total > 0:
                pbar.set_postfix({
                    "passed": n_passed, 
                    "normal_filtered": n_filtered_normal,
                    "multi_filtered": n_filtered_multi,
                    "ratio": f"{(n_filtered_multi + n_filtered_normal) / total * 100:.3f}%"
                })
    
        return final_results
