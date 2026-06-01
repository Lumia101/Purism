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
import os
from purism import PurifyConfig, UnicodeCleaner, UICleaner, TextCleaner, HarmfulWordsFilter, SpamWordsFilter
from datasets import load_dataset
from tqdm.auto import tqdm

# Load dataset
ds = load_dataset(
    "allenai/c4",
    "ko",
    split="train",
    streaming=True
).take(1000)

# Load normalization techniques
norms = [
    UnicodeCleaner("NFC"),
    UICleaner(),
    TextCleaner()
]

# Load filters
fast_filters = [
    HarmfulWordsFilter(3),
    SpamWordsFilter(4),
    DedupFilter()
]

heavy_filters = [
    PPLFilter()
]

# Load the previously defined filters and normalization techniques into PurifyConfig.
purifier = PurifyConfig(
    norms,
    fast_filters,
    heavy_filters
)

all_list = []

for text in ds:
    all_list.append(ds["text"])

result = purifier.parallel_purify(all_list, os.cpu_count()) # Apply the normalization technique and filters loaded in PurifyConfig.

print("=" * 200)

for i in range(20):
    print(f"Sample {i + 1} (passed: {result[i]["passed"]}): {result[i]["text"]}")
    print("=" * 200)
```
You can see that corpus marked as "passed: True" are better than corpus marked as "passed: False".

## API
This library contains many more types of filters in addition to the two mentioned earlier. If you would like to see more features, please visit [this page.](https://github.com/Lumia101/Purism/blob/main/API.md)

# Limitations

* This library can accurately filter only Korean text. Modification of the source code is required to use other languages.
* This library is not always accurate. It can filter out non-harmful corpora, but may fail to filter out some harmful corpora.
