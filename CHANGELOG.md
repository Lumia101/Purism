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
> Improved processing speed through multi-core processing

## Pipeline
* Changes to function names and additions to features in PurifyConfig
  * Added parallel_purify function
    * You can perform multi-core processing with this single instruction.
  * Separate the purify function into fast_purify and heavy_purify.
    * heavy_purify recommends using a GPU.

## Filter
* Adjust to prevent memory usage from skyrocketing due to multi-core processing
  * Due to this, PPLFilter does not support multi-core processing.