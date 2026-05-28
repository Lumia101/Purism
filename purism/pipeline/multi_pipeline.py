import multiprocessing
from concurrent.futures import ProcessPoolExecutor
from typing import List, Dict, Any
from purism.normalizers.normalizer import TextCleaner, UICleaner, UnicodeCleaner
from purism.filters.simple_filter import LengthFilter, HarmfulWordsFilter, SpamWordsFilter, SignAbuseFilter, PIIFilter
from purism.filters.advanced_filter import LanguageFilter, DedupFilter
from purism.filters.model_filter import PPLFilter

_global_config = None

def _init_worker(filters, normalizer):
    global _global_config
    for f in filters:
        if hasattr(f, 'load_model'):
            f.load_model()
    _global_config = {
        "filters": filters,
        "normalizer": normalizer
    }

def _worker_task(text: str):
    global _global_config
    filters = _global_config["filters"]
    normalizers = _global_config["normalizer"]
    
    text_cleaned = text
    for n in normalizers:
        text_cleaned = n.normalize(text_cleaned)

    for f in filters:
        if not f.apply(text_cleaned):
            return {
                "raw_text": text,
                "passed": False,
                "filtered_by": f.__class__.__name__,
                "normalized_text": text_cleaned
            }
    
    return {
        "raw_text": text,
        "passed": True,
        "filtered_by": None,
        "normalized_text": text_cleaned
    }

class PurifyConfig:
    def __init__(self, filters, normalizer):
        self.normalizer = normalizer
        self.filters = filters

    def multi_purify(self, texts: List[str], n_process: int = None, chunksize: int = 10):
        if n_process is None:
            n_process = multiprocessing.cpu_count() 

        with ProcessPoolExecutor(
            max_workers=n_process,
            initializer=_init_worker,
            initargs=(self.filters, self.normalizer)
        ) as executor:
            results = list(executor.map(_worker_task, texts, chunksize=chunksize))
        
        return results
