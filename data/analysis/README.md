# Analysis System Improvements

This document outlines recent improvements to the analysis visualization system.

## Overview of Changes

We have enhanced the analysis visualization system with the following improvements:

1. **Advanced Raw Data Processing**: Added direct support for processing raw MapReduce output files, eliminating the need for pre-processed summary files.

2. **Intelligent Brand/Model Classification**: Implemented smart classification for car brands and models, properly categorizing entries based on known brands and models, as well as pattern-based heuristics.

3. **Duplicate Elimination**: Added deduplication logic to combine counts for the same brand/model mentioned in different contexts (brand_comment, brand, total, etc.).

4. **Vehicle Model Analysis**: Fixed the empty vehicle model analysis section by extracting model data from brand mentions and generating estimated model data when explicit model data is not available.

5. **Automatic Index Generation**: Created robust scripts (both PowerShell and Batch) to automatically scan for analysis files and generate the necessary index and summary files.

## Usage Instructions

### Running Analysis Index Generator

Two options are available for generating the analysis index:

#### Option 1: Windows Batch Script
```
cd data/analysis
update_index.bat
```

#### Option 2: PowerShell Script
```
cd data/analysis
powershell -ExecutionPolicy Bypass -File list_analyses.ps1
```

Both scripts will:
1. Scan all analysis directories
2. Generate an `analyses_index.json` file in the web data directory
3. Create summary JSON files for each analysis if they don't exist
4. Display a summary of found analyses

### Directory Structure

The analysis system expects directories to follow this naming convention:
```
<dataset>_<datadate>_<rundate>_<analysistype>
```

Example: `drivingsg_data_20250318_143009_brands_20250403_195039`

### Data Processing

The system now intelligently processes raw MapReduce output files (part-r-00000) with the following improvements:

1. **Brand Analysis**:
   - Identifies and deduplicates car brand mentions
   - Uses a dictionary of known car brands for accurate classification
   - Intelligently separates brand vs. model mentions

2. **Model Analysis**:
   - Identifies car models based on known models for popular brands
   - Uses pattern matching to identify potential model names
   - Generates plausible model data from brand mentions when model data is not available

## Technical Details

### Raw Data Processing

The system now directly parses the `part-r-00000` files using the format:
```
key\tvalue
```

Where keys can have prefixes like:
- `brand:`
- `brand_comment:`
- `model:`
- `total:`

The system extracts, normalizes, and classifies these entries to generate structured data for visualization.

### Brand/Model Classification Logic

The classification system uses multiple strategies:
1. Explicitly labeled keys (brand:, model:)
2. Dictionary lookup of known brands and models
3. Pattern-based heuristics:
   - Models often contain numbers or hyphens
   - Models often have multi-word names
   - Brands are typically single words

This ensures accurate representation in the brand and model charts.

### Index File Format

The analysis index file uses the following format:
```json
{
  "analyses": [
    {
      "dataset": "dataset_datadate",
      "data_date": "datadate",
      "run_date": "rundate",
      "analysis_type": "analysistype",
      "summary_file": "/static/data/dataset_datadate_rundate_analysistype/summary.json",
      "output_dir": "../../data/analysis/dataset_datadate_rundate_analysistype"
    },
    ...
  ]
}
```

This allows the visualization system to locate and process all available analyses. 