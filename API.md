# Pipeline

## class **PurifyConfig():**

> def **__init__(normalizer, filter_multi, filter_normal, batch_size=16):**
> 
|value|type|function|
|:-------------|:------:|:---------------|
|normalizer|list|Receive a list of normalization techniques to apply.|
|filter_multi|list|Receives filters capable of multicore processing.|
|filter_normal|list|Receives filters that cannot be processed by multicore processing.|
|batch_size|int|Receives the batch size to be used in batch processing.|

> def **parallel_purify(texts, n_process=-1):**

|value|type|function|
|:-------------|:------:|:---------------|
|texts|list|Receives the texts to apply filtering.|
|n_process|int|Receive the number of cores to use.|

Rapidly apply normalization and filters through multi-core processing.

> **Return value**
```Python
({
    "passed": bool, # Returns False for harmful document and True for harmless documents.
    "filtered_by": str or None, # Returns a filter that filters the input document, and returns None if "passed" is true.
    "text": str # Document after normalization from "raw_text"
})
```

---

# Normalizers

## class **BaseNormalizer(ABC):**

> def **normalize(text):**

|value|type|function|
|:-------------|:------:|:---------------|
|text|str|Receives the text to normalize.|

The base class for all normalization classes.

---

## class **UnicodeCleaner(BaseNormalizer):**

> def **__init__(type="NFC"):**

|value|type|function|
|:-------------|:------:|:---------------|
|type|str|Select the Unicode normalization method to use.|

> def **normalize(text):**

|value|type|function|
|:-------------|:------:|:---------------|
|text|str|Receives the text to normalize.|

This command performs Unicode-based normalization.

> **Return value**
```Python
str # Returns the document after Unicode-based normalization.
```

---

## class **UICleaner(BaseNormalizer):**

> def **__init__():**

> def **normalize(text):**

|value|type|function|
|:-------------|:------:|:---------------|
|text|str|Receives the text to normalize.|

This command removes debris, such as HTML code, that interferes with AI learning.

> **Return value**
```Python
str # Returns document with debris such as HTML code removed
```

---

## class **TextCleaner(BaseNormalizer):**

> def **__init__():**

> def **normalize(text):**

|value|type|function|
|:-------------|:------:|:---------------|
|text|str|Receives the text to normalize.|

This command corrects characters that are repeated too many times or broken characters.

> **Return value**
```Python
str # Returns a document with reduced use of duplicate characters and broken characters removed.
```

# Filters

## class **BaseFilter(ABC):**

> def **apply(text):**

|value|type|function|
|:-------------|:------:|:---------------|
|text|str|Receives the text to filter.|

The base class for all filter classes.

---

## class **LengthFilter(BaseFilter):**

> def **__init__(min_len=50, max_len=10000):**

|value|type|function|
|:-------------|:------:|:---------------|
|min_len|int|Filters all corpora with a length less than the set value.|
|max_len|int|Filters all corpora with a length greater than the set value.|

> def **apply(text):**

|value|type|function|
|:-------------|:------:|:---------------|
|text|str|Receives the text to filter.|

This command filters documents that exceed the set character count range.

> **Return value**
```Python
bool # Returns False if the text length is outside the set range, otherwise True.
```

---

## class **HarmfulWordsFilter(BaseFliter):**

> def **__init__(threshold=5):**

|value|type|function|
|:-------------|:------:|:---------------|
|threshold|int|Set how many harmful words to allow.|

> def **apply(text):**

|value|type|function|
|:-------------|:------:|:---------------|
|text|str|Receives the text to filter.|

This command filters documents containing more than a set number of harmful words.
(You can check the harmful words [here](https://github.com/Lumia101/Purism/blob/main/purism/resources/harmful_words.txt). If you think I missed any words, please contact the developer.)

> **Return value**
```Python
bool # Returns False if harmful words are used more than the set value, and True otherwise.
```

---

## class **SpamWordsFilter(BaseFilter):**

> def **__init__(threshold=8):**

|value|type|function|
|:-------------|:------:|:---------------|
|threshold|int|Set how many harmful words to allow.|

> def **apply(text):**

|value|type|function|
|:-------------|:------:|:---------------|
|text|str|Receives the text to filter.|

This command filters documents where words commonly found in spam documents appear above a set value.
(You can check the spam words [here](https://github.com/Lumia101/Purism/blob/main/purism/resources/spam_words.txt). If you think I missed any words, please contact the developer.)

> **Return value**
```Python
bool # Returns False if spam words are used more than the set value, and True otherwise.
```

---

## class **SignAbuseFilter(BaseFilter):**

> def **__init__(threshold=0.3):**

|value|type|function|
|:-------------|:------:|:---------------|
|threshold|float|Sets the allowance ratio for special characters.|

> def **apply(text):**

|value|type|function|
|:-------------|:------:|:---------------|
|text|str|Receives the text to filter.|

This command filters documents that use an excessive amount of symbols.

> **Return value**
```Python
bool # Returns False if the number of symbols used relative to the length of the entire document exceeds the set level, otherwise True.
```

---

## class **PIIFilter(BaseFilter):**

> def **__init__():**

> def **apply(text):**

|value|type|function|
|:-------------|:------:|:---------------|
|text|str|Receives the text to filter.|

This command filters documents containing important personal information.

> **Return value**
```Python
bool # Returns False if the document contains personal information, otherwise True.
```

---

## class **LanguageFilter(BaseFilter):**

> def **__init__(threshold=0.6):**

|value|type|function|
|:-------------|:------:|:---------------|
|threshold|float|Sets how strictly to measure whether the corpus is Korean.|

> def **apply(text):**

|value|type|function|
|:-------------|:------:|:---------------|
|text|str|Receives the text to filter.|

This command filters non-Korean documents.

> **Return value**
```Python
bool # Returns False if the reading result indicates that it is not Korean, otherwise returns True.
```

---

## class **DedupFilter(BaseFilter):**

> def **__init__(threshold=0.7, num_perm=128, shingles=3):**

|value|type|function|
|:-------------|:------:|:---------------|
|threshold|float|Sets how strictly to measure similarity between sentences.|
|num_perm|int|Sets the length of the hash function. If set too long, the speed slows down, and if set too short, performance decreases.|
|shingles|int|Sets how finely the corpus is split. A lower value splits it more finely.|

> def **apply(text):**

|value|type|function|
|:-------------|:------:|:---------------|
|text|str|Receives the text to filter.|

This command filters duplicate documents within the data.

> **Return value**
```Python
bool # Returns False if a document with similar content already exists, otherwise True.
```

---

## class **PPLFilter(BaseFilter):**

> def **__init__(ppl_threshold=400.0, batch_size=16):**

|value|type|function|
|:-------------|:------:|:---------------|
|ppl_threshold|float|Determines how high the level of bewilderment must be to filter. The appropriate value varies depending on the type of data.|
|batch_size|int|Receives the batch size during batch processing.|

> def **apply(text):**

|value|type|function|
|:-------------|:------:|:---------------|
|text|list[str]|Receives the text to filter.|

This command filters documents where the sentence's perplexity is above a certain value.

> **Return value**
```Python
bool # Returns False if the perplexity measurement result is greater than or equal to the set value, otherwise True.
```
