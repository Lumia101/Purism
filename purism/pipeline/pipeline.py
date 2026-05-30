# Import all created Python codes from this repository
from joblib import Parallel, delayed
from tqdm.auto import tqdm

from purism.normalizers.normalizer import TextCleaner, UICleaner, UnicodeCleaner
from purism.filters.simple_filter import (
    LengthFilter,
    HarmfulWordsFilter,
    SpamWordsFilter,
    SignAbuseFilter,
    PIIFilter,
)
from purism.filters.advanced_filter import LanguageFilter, DedupFilter, PPLFilter


# Setting Settings for Data Purification
class PurifyConfig:
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
                    "text": text_cleaned,
                }

        return {
            "passed": True,
            "filtered_by": None,
            "text": text_cleaned,
        }

    def normal_purify_batch(self, batch_results: list[dict]):
        """
        Apply the second-stage filters to a batch of already-normalized texts.

        This method keeps the original order of batch_results and updates each
        item in-place with the first filter that rejects it.
        """
        if not batch_results:
            return batch_results

        for flt in self.filter_normal:
            current_indices = [
                i for i, item in enumerate(batch_results) if item["passed"]
            ]
            if not current_indices:
                break

            texts = [batch_results[i]["text"] for i in current_indices]

            if isinstance(flt, PPLFilter):
                pass_flags = flt.apply_batch(texts)
            else:
                pass_flags = [flt.apply(text) for text in texts]

            for idx, passed in zip(current_indices, pass_flags):
                if not passed:
                    batch_results[idx]["passed"] = False
                    batch_results[idx]["filtered_by"] = flt.__class__.__name__

        return batch_results

    def parallel_purify(self, texts: list, n_process=-1):
        n_passed = 0
        n_filtered_multi = 0
        n_filtered_normal = 0
        total = len(texts)

        pbar1 = tqdm(texts, desc="Applying MultiCore filter", total=total)

        fast_results = Parallel(
            n_jobs=n_process,
            backend="threading",
            return_as="generator",
        )(
            delayed(self.multi_purify)(text) for text in pbar1
        )

        buffer = []
        pbar2 = tqdm(desc="Applying Normal filter", total=total)

        for text in fast_results:
            if not text["passed"]:
                n_filtered_multi += 1
                yield text
                pbar2.update(1)
                continue

            buffer.append(text)

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
                pbar2.set_postfix(
                    {
                        "passed": n_passed,
                        "normal_filtered": n_filtered_normal,
                        "multi_filtered": n_filtered_multi,
                        "ratio": f"{(n_filtered_multi + n_filtered_normal) / (n_filtered_multi + n_filtered_normal + n_passed) * 100:.3f}%",
                    }
                )

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
