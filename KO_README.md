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
from purism import PurifyConfig, UnicodeCleaner, UICleaner, TextCleaner, HarmfulWordsFilter, SpamWordsFilter
from datasets import load_dataset
from tqdm.auto import tqdm

# 데이터셋을 불러옵니다.
ds = load_dataset(
    "allenai/c4",
    "ko",
    split="train",
    streaming=True
).take(100)

# 정규화 명령어들을 불러옵니다.
norms = [
    UnicodeCleaner("NFC"),
    UICleaner(),
    TextCleaner()
]

# 필터들을 불러옵니다.
filters = [
    HarmfulWordsFilter(3),
    SpamWordsFilter(4)
]

# PurifyConfig에 필터들과 정규화 명령어들을 장착합니다.
purifier = PurifyConfig(filters, norms)

passed = []
filtered = []

for text in tqdm(ds, desc="Filtering...", total=100):
    result = purifier.purify(text["text"]) # PurifyConfig에 장착된 정규화 명령어들을 적용한 후, 필터링을 진행합니다.
    if result["passed"]:
        passed.append(result["raw_text"])
    else:
        filtered.append(result["raw_text"])

print("=" * 200)

# 검열되지 않은 문서들 출력
for i in range(10):
    print(f"Sample {i + 1} (passed): {passed[i]}")
    print("=" * 200)

# 검열된 문서들 출력
for i in range(10):
    print(f"Sample {i + 1} (filtered): {filtered[i]}")
    print("=" * 200)
```
"passed" 라고 마킹되어 있는 문서들의 품질이 "filtered"라고 마킹되어 있는 문서들의 품질보다 확실히 좋음을 알 수 있습니다.

## API
이 라이브러리는 앞서 설명한 코드에 있는 요소들 외에도 다양한 정규화 방식과 필터를 제공합니다. 더 많은 기능들을 확인하려면 [여기서 확인하세요.](https://github.com/Lumia101/Purism/blob/main/API.md)

# 한계

* 이 라이브러리는 한국어 텍스트만 필터링할 수 있습니다. 다른 언어의 필터링을 위해서는 대규모 코드 수정이 필요합니다.
* 이 라이브러리는 완벽하지 않습니다. 정상적인 문서를 필터링할 수도 있고, 유해한 문서를 필터링하지 못할 수 있습니다.
