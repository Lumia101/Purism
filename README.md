# Purism: Automatic data filtering library specialized in Korean data purification
> **Puri**fy **s**yste**m**

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
from purism import PurifyConfig, UnicodeCleaner, UICleaner, TextCleaner, HarmfulWordsFilter, SpamWordsFilter
from datasets import load_dataset
from tqdm.auto import tqdm

# Load dataset
ds = load_dataset(
    "allenai/c4",
    "ko",
    split="train",
    streaming=True
).take(100)

# Load normalization techniques
norms = [
    UnicodeCleaner("NFC"),
    UICleaner(),
    TextCleaner()
]

# Load filters
filters = [
    HarmfulWordsFilter(3),
    SpamWordsFilter(4)
]

# Load the previously defined filters and normalization techniques into PurifyConfig.
purifier = PurifyConfig(filters, norms)

passed = []
filtered = []

for text in tqdm(ds, desc="Filtering...", total=100):
    result = purifier.purify(text["text"]) # Apply the normalization techniques and filters loaded in PurifyConfig.
    if result["passed"]:
        passed.append(result["raw_text"])
    else:
        filtered.append(result["raw_text"])

print("=" * 200)

# Uncensored corpora
for i in range(10):
    print(f"Sample {i + 1} (passed): {passed[i]}")
    print("=" * 200)

# Censored corpora
for i in range(10):
    print(f"Sample {i + 1} (filtered): {filtered[i]}")
    print("=" * 200)
```
You can see that corpus marked as "passed" are better than corpus marked as "filtered".

## API
This library contains many more types of filters in addition to the two mentioned earlier. If you would like to see more features, please visit [this page.](https://github.com/Lumia101/Purism/blob/main/API.md)
