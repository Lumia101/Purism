# Import all created Python codes from this repository
from joblib import Parallel, delayed
from tqdm.auto import tqdm
from purism.normalizers.normalizer import TextCleaner, UICleaner, UnicodeCleaner
from purism.filters.simple_filter import LengthFilter, HarmfulWordsFilter, SpamWordsFilter, SignAbuseFilter, PIIFilter
from purism.filters.advanced_filter import LanguageFilter, DedupFilter, PPLFilter

# Setting Settings for Data Purification
class PurifyConfig():
    def __init__(self, normalizer, filter_multi, filter_normal, batch_size=16):
        self.normalizer = normalizer
        self.filter_multi = filter_multi
        self.filter_normal = filter_normal
        self.batch_size = batch_size

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
        texts = [r["text"] for r in batch_results]

        for flt in self.filter_normal:
            pass_flags = flt.apply(texts) 
                                                
            for i, passed in enumerate(pass_flags):
                if not passed:
                    batch_results[i]["passed"] = False
                    batch_results[i]["filtered_by"] = flt.__class__.__name__
                                                                                                                            
            return batch_results

    def parallel_purify(self, texts: list, n_process=-1):
        n_passed = 0
        n_filtered_multi = 0
        n_filtered_normal = 0
        total = len(texts)

        pbar1 = tqdm(texts, desc="Applying MultiCore filter", total=total)

        fast_results = Parallel(n_jobs=n_process, backend="threading", return_as="generator")(
            delayed(self.multi_purify)(text) for text in pbar1
        )

        buffer = []
        pbar2 = tqdm(desc="Applying Normal filter", total=total)
        
        for text in fast_results:
            if not text["passed"]:
                text_p = self.normal_purify(text["text"])

                n_filtered_multi += 1
                yield text
                pbar2.update(1)
                continue
            
            buffer.append(res)

            if len(buffer) >= self.batch_size:
                processed_batch = self.normal_purify_batch(buffer)
                for item in processed_batch:
                    if item["passed"]:
                        n_passed += 1
                    else:
                        n_filtered_normal += 1
                    yield item
                    pbar2.update(1)
                buffer = []
            
            if n_filtered_multi + n_filtered_normal + n_passed > 0:
                pbar2.set_postfix({
                    "passed": n_passed, 
                    "normal_filtered": n_filtered_normal,
                    "multi_filtered": n_filtered_multi,
                    "ratio": f"{(n_filtered_multi + n_filtered_normal) / (n_filtered_multi + n_filtered_normal + n_passed) * 100:.3f}%"
                })

        if buffer:
            processed_batch = self.normal_purify_batch(buffer)
            for item in processed_batch:
                if item["passed"]:
                    n_passed += 1
                else:
                    n_filtered_normal += 1
                yield item
                pbar2.update(1)

        pbar2.close()