# Purism: 한국어 데이터 정제에 특화된 데이터 필터링 라이브러리
> **Puri**fy **s**yste**m**

## 개요
이 리포지토리는 한국어 데이터 정제에 특화된 데이터 필터링 라이브러리입니다.
 
# 사용 방법

## 설치
**pip를 통해 설치하기**
```bash
pip install purism
```

## 빠른 시작
[C4 데이터셋](https://huggingface.co/datasets/allenai/c4)은 이름에 **"Clean"** 이라고 되어 있지만, **전혀 "clean" 하지 않습니다.** (특히 한국어 서브셋은 더더욱 그렇습니다.) 이 코드는 C4 데이터셋에 추가적인 필터링을 적용하는 코드입니다.

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
이 코드를 실행한 후 결과를 보면 필터링 된 텍스트들이 많음을 알 수 있습니다.이 코드를 실행한 후 결과를 보면 필터링 된 텍스트들이 많음을 알 수 있습니다.

## API
더 많은 기능들은 [이 페이지](https://github.com/Lumia101/Purism/blob/main/API.md)에서 찾을 수 있습니다.

# 한계
* 이 라이브러리는 한국어 텍스트만 필터링할 수 있습니다. 다른 언어의 필터링을 위해서는 대규모 코드 수정이 필요합니다.
* 이 라이브러리는 완벽하지 않습니다. 정상적인 문서를 필터링할 수도 있고, 유해한 문서를 필터링하지 못할 수 있습니다.
