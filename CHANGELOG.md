# v1.0.0
> Initial Release

## Filters
* Add 5 Heurstic Filter (Simple Filter)
* Add 2 Statisic Filter (Advanced Filter)
* Add 1 Model-Based Filter (Model Filter)

## Normalizers
* Add 3 Normalizers (Unicode, UI, Text)

# v1.0.1
> Bug fixes

## Filters
* Fixed an issue where an error occurred when calling DedupFilter.

# v1.0.2
> Bug fixes

## Normalizers
* Fixed an issue where only one normalization command was applied at a time.

# v2.0.0
> Improve data processing speed

## Pipeline
* Added multi-core processing and batch processing capabilities
  * It is available through the parallel_purify() function.
  * As a result, the filtering result is returned in generator format.

## Filter
* Modified various filter logics to suit the parallel_purify() environment.
* Integrated advanced_filter.py and model_filter.py.
* Removed quantization and reduced the model size.

# v2.1.0
> Reduce model size and processing speed further

## Pipeline
* Replace multi-core processing method (threading -> loky)
* Replace the PPL measurement model with a lighter model