# Pipeline

class **PurifyConfig():**

> def **__init__(filters, normalizer):**
> 
|value|type|function|
|:-------------|:------:|:---------------|
|filters|list|Receive a list of filters to apply.|
|normalizer|list|Receive a list of normalization techniques to apply.|

> def **purify(text):**

|value|type|function|
|:-------------|:------:|:---------------|
|text|str|Receives the text to apply filtering.|

> **Return value**
```Python
return {
    "raw_text": str,
    "passed": bool,
    "filtered_by": Filter name(str) or None,
    "normalized_text": str
}
```

# Normalizers

class **BaseNormalizer(ABC):**

> def **normalize(text):**

|value|type|function|
|:-------------|:------:|:---------------|
|text|str|Receives the text to normalize.|

The base class for all normalization classes.

---

class **UnicodeCleaner(BaseNormalizer):**

> def **__init__(type="NFC"):**

|value|type|function|
|:-------------|:------:|:---------------|
|type|str|Select the Unicode normalization method to use.|

> def **normalize(text):**

|value|type|function|
|:-------------|:------:|:---------------|
|text|str|Receives the text to normalize.|

> **Return value**
```Python
return str
```

---

class **UICleaner(BaseNormalizer):**

> def **__init__():**

> def **normalize(text):**

|value|type|function|
|:-------------|:------:|:---------------|
|text|str|Receives the text to normalize.|

> **Return value**
```Python
return str
```

---

class **TextCleaner(BaseNormalizer):**

> def **__init__():**

> def **normalize(text):**

|value|type|function|
|:-------------|:------:|:---------------|
|text|str|Receives the text to normalize.|

> **Return value**
```Python
return str
```

# Filters

class **BaseFilter(ABC):**

> def **apply(text):**

|value|type|function|
|:-------------|:------:|:---------------|
|text|str|Receives the text to filter.|

The base class for all filter classes.

---

class **LengthFilter(BaseFilter):**

> def **__init__(min_len=50, max_len=10000):**

|value|type|function|
|:-------------|:------:|:---------------|
|min_len|int|Filters all corpora with a length less than the set value.|
|max_len|int|Filters all corpora with a length greater than the set value.|

> def **apply(text):**

|value|type|function|
|:-------------|:------:|:---------------|
|text|str|Receives the text to filter.|

> **Return value**
```Python
return bool
```

---

class **HarmfulWordsFilter(BaseNormalizer):**

> def **__init__(threshold=5):**

|value|type|function|
|:-------------|:------:|:---------------|
|threshold|int|Set how many harmful words to allow.|

> def **apply(text):**

|value|type|function|
|:-------------|:------:|:---------------|
|text|str|Receives the text to filter.|

> **Return value**
```Python
return bool
```

---

class **SpamWordsFilter(BaseNormalizer):**

> def **__init__(threshold=8):**

|value|type|function|
|:-------------|:------:|:---------------|
|threshold|int|Set how many harmful words to allow.|

> def **apply(text):**

|value|type|function|
|:-------------|:------:|:---------------|
|text|str|Receives the text to filter.|

> **Return value**
```Python
return bool
```

---

class **SignAbuseFilter(BaseNormalizer):**

> def **__init__(threshold=0.3):**

|value|type|function|
|:-------------|:------:|:---------------|
|threshold|float|Sets the allowance ratio for special characters.|

> def **apply(text):**

|value|type|function|
|:-------------|:------:|:---------------|
|text|str|Receives the text to filter.|

> **Return value**
```Python
return bool
```

---

class **PIIFilter(BaseNormalizer):**

> def **__init__():**

> def **normalize(text):**

|value|type|function|
|:-------------|:------:|:---------------|
|text|str|Receives the text to filter.|

> **Return value**
```Python
return bool
```
