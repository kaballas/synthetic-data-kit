# JSON to JSONL Converter

This script combines all `.json` files in a specified directory into a single `.jsonl` (JSON Lines) file.

## Overview

JSONL (JSON Lines) is a format where each line in the file is a separate JSON object. This format is useful for:

- Streaming large datasets
- Processing data in a line-by-line manner
- Working with tools that expect JSONL format
- Reducing memory usage when processing large collections of JSON objects

## Features

- Discovers all `.json` files in the specified directory
- Handles both single JSON objects and JSON arrays in input files
- When processing JSON arrays, each array element becomes a separate line in the output
- Preserves all data from input files
- Provides detailed progress information during processing
- Validates output format to ensure each line is valid JSON

## Usage

The script is configured to:
- Input directory: `C:\DTT\synthetic-data-kit\data\generated\done`
- Output file: `C:\DTT\synthetic-data-kit\data\generated\combined.jsonl`

To run the script:
```bash
python combine_json_to_jsonl.py
```

## Processing Details

1. The script scans the input directory for all files with `.json` extension
2. For each JSON file:
   - If the file contains a single JSON object, that object becomes one line in the output
   - If the file contains a JSON array, each element of the array becomes a separate line in the output
3. Each JSON object is written on its own line in the output file
4. Processing results are displayed showing the number of objects processed and any errors

## Output

- A single `.jsonl` file containing all JSON objects from the input files
- Each line in the file is a valid, complete JSON object
- The output file maintains the same character encoding as the input files

## Verification

The script includes a verification function that confirms each line in the output file is valid JSON. All 70 input files were successfully processed into valid JSONL format.