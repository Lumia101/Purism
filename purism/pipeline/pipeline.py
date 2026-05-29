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
        n_filtered = 0
        with tqdm(texts, desc="Applying fast filter", total=len(texts), unit="texts") as pbar_cpu:
            def fast_purify_trace(text):
                result = self.fast_purify(text)
                if result["passed"]:
                    n_passed += 1
                else:
                    n_filtered += 1
                pbar_cpu.update(1)
                pbar_cpu.set_postfix({
                    "passed": n_passed,
                    "filtered": n_filtered,
                    "filtered_ratio": f"{n_filtered / (n_passed + n_filtered) * 100:.3f}%"
                })
                return result

        parallel = Parallel(n_jobs=n_process)
        fast_results = parallel(
            delayed(fast_purify_trace)(text) for text in texts
        )

        n_remain = n_passed
        n_passed = 0
        n_filtered = 0

        pbar_gpu = tqdm(fast_results, desc="Applying heavy filter", total=n_remain, unit="texts")

        for text in pbar_gpu:
            if text["passed"]:
                final_results.append(self.heavy_purify(text["text"]))
                n_passed += 1
            else:
                final_results.append(text)
                n_filtered += 1

            pbar_gpu.update(1)
            pbar_gpu.set_postfix({
                "passed": n_passed,
                "filtered": n_filtered,
                "filtered_ratio": f"{n_filtered / (n_passed + n_filtered) * 100:.3f}%"
            })
    
        return final_result