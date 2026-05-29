# Import all created Python codes from this repository
from joblib import Parallel, delayed
from tqdm.auto import tqdm
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
        n_passed = 0
        n_filtered_cpu = 0
        n_filtered_gpu = 0
        final_results = []

        fast_results = Parallel(n_jobs=n_process)(
            delayed(self.fast_purify)(text) for text in tqdm(texts, desc="Applying fast filter", unit="texts")
        )

        pbar = tqdm(fast_results, desc="Applying heavy filter", unit="texts")
        
        for text in pbar:
            if text["passed"]:
                text_p = self.heavy_purify(text["text"])
                final_results.append(text_p)

                if text_p["passed"]:
                    n_passed += 1
                else:
                    n_filtered_gpu += 1
            else:
                final_results.append(text)
                n_filtered_cpu += 1

            total = len(texts)
            
            if total > 0:
                pbar.set_postfix({
                    "passed": n_passed, 
                    "gpu_filtered": n_filtered_gpu,
                    "cpu_filtered": n_filtered_cpu,
                    "ratio": f"{(n_filtered_cpu + n_filtered_gpu) / total * 100:.3f}%"
                })
    
        return final_results
