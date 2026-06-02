# Purism: Automatic data filtering library specialized in Korean data purification
> **Puri**fy **s**yste**m**

[View in Korean](https://github.com/Lumia101/Purism/blob/main/KO_README.md)

## Summary
This repository is an automatic data filtering library specialized in Korean data purification.
 
# How to use

## Installation
**Installation using pip**
```bash
pip install purism
```

## Quickstart
[C4 dataset](https://huggingface.co/datasets/allenai/c4) has **"Clean"** in its name, but it is **NOT clean** at all (especially the Korean subset). This is a code that performs **additional filtering** on the C4 dataset using this library.

```Python
from datasets import load_dataset
from collections import Counter
from tqdm.auto import tqdm
from purism import PurifyConfig, UnicodeCleaner, UICleaner, TextCleaner, LengthFilter, HarmfulWordsFilter, SpamWordsFilter, SignAbuseFilter, PIIFilter, LanguageFilter, DedupFilter

take_count = 40000
batch_size = 64

print("=" * 100)
ds = load_dataset(
    "allenai/c4",
    "ko",
    split="train",
    streaming=True
).take(take_count)

ds_sample = []

for text in tqdm(ds, desc="Extracting texts", total=take_count):
    ds_sample.append(text["text"])

normalizers = [
    UnicodeCleaner("NFC"),
    UICleaner(),
    TextCleaner()
]

multi_filters = [
    LengthFilter(50, 8000),
    HarmfulWordsFilter(4),
    SpamWordsFilter(6),
    SignAbuseFilter(0.2),
    PIIFilter()
]

batch_filters = [
    LanguageFilter(),
    DedupFilter()
]

counter = Counter()
filtered_all = 0
n_passed = 0
passed = []
n_filtered = 0
filtered = []
reason = []
purifier = PurifyConfig(normalizers, multi_filters, batch_filters, batch_size)

print("=" * 100)
result = purifier.parallel_purify(ds_sample, -1)

for text in result:
    if text["passed"]:
        counter["Passed"] += 1
        if n_passed < 10:
            passed.append(text["text"])
            n_passed += 1
    else:
        filtered_all += 1
        counter[text["filtered_by"]] += 1
        if n_filtered < 10:
            filtered.append(text["text"])
            reason.append(text["filtered_by"])
            n_filtered += 1

print("=" * 100)
print("Purification complete!")
print("=" * 100)
print("<|Filtering statistics|>")
print(" ")
print(f"Passed: {counter["Passed"]:,} ({counter["Passed"] / take_count:.3f}%)")
print(f"LengthFilter: {counter["LengthFilter"]:,} ({counter["LengthFilter"] / take_count:.3f}%)")
print(f"HarmfulWordsFilter: {counter["HarmfulWordsFilter"]:,} ({counter["HarmfulWordsFilter"] / take_count:.3f}%)")
print(f"SpamWordsFilter: {counter["SpamWordsFilter"]:,} ({counter["SpamWordsFilter"] / take_count:.3f}%)")
print(f"SignAbuseFilter: {counter["SignAbuseFilter"]:,} ({counter["SignAbuseFilter"] / take_count:.3f}%)")
print(f"PIIFilter: {counter["PIIFilter"]:,} ({counter["PIIFilter"] / take_count:.3f}%)")
print(f"LanguageFilter: {counter["LanguageFilter"]:,} ({counter["LanguageFilter"] / take_count:.3f}%)")
print(f"DedupFilter: {counter["DedupFilter"]:,} ({counter["DedupFilter"] / take_count:.3f}%)")
print(f"Total number of filtered texts: {filtered_all:,} ({filtered_all / take_count:.3f}%)")
print("=" * 100)
```
If you look at the results after running this code, you can see that there are many filtered texts.

## API
More features can be found on [this page.](https://github.com/Lumia101/Purism/blob/main/API.md)

# Limitations
* This library can accurately filter only Korean text. Modification of the source code is required to use other languages.
* This library is not always accurate. It can filter out non-harmful corpora, but may fail to filter out some harmful corpora.
