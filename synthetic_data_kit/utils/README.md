# SAP Research Reports Exporter

This script exports each record from the "Kaballas/SAP_NEW" Hugging Face dataset field "research_report" into its own .txt file using the "Title" field as the file name.

## Prerequisites

- Python 3.x installed
- datasets package (from Hugging Face):  
  Run `pip install datasets`

## How It Works

1. The script loads the "Kaballas/SAP_NEW" dataset from Hugging Face
2. Creates a directory called "research_reports_txt" to store output files
3. Iterates through each record in the dataset
4. Sanitizes the "Title" field to create valid file names (removes invalid characters and limits length)
5. Exports the "research_report" content to a text file named after the sanitized title

## Features

- Sanitizes file names to remove/replace invalid characters for file systems (especially Windows: \ / * ? " < > | :)
- Limits file name length to 100 characters for OS compatibility
- Handles potential duplicate filenames by adding a counter suffix
- Provides progress updates during the export process
- Handles missing or empty titles by creating a default name

## Output

The script creates 408 individual text files in the `research_reports_txt/` directory, each containing the research report content from the dataset, with filenames derived from the corresponding titles. The script properly handles:

- Windows-incompatible characters such as colons (:) by replacing them with underscores (_)
- Duplicate filenames by appending a counter suffix (e.g., `_1`, `_2`, etc.)
- Special Unicode characters through proper encoding handling
- Titles that might be empty or contain only whitespace

## JSON to JSONL Converter

Additionally, a separate script was created to combine all .json files in `C:\DTT\synthetic-data-kit\data\generated\done` into a single JSONL file. This script:

- Found and processed 70 .json files
- Combined them into a single `combined.jsonl` file in the `C:\DTT\synthetic-data-kit\data\generated` directory
- Created 70 valid JSON lines, one for each input file
- Preserves all data from the original JSON files in the JSONL format

## Fields Used

- `Title`: Used as the filename for each exported text file
- `research_report`: Contains the content that gets exported to each text file

## Usage

Run the script with:
```bash
python export_hf_dataset.py
```

## Notes

- The dataset contains 408 records with the following columns: 
  ['Description', 'Title', 'Area', 'Product', 'SeeMoreLink', 'DemoLink', 
  'research_instructions', 'research_report', 'processed']
- All records were successfully exported with 0 errors
- The script uses the "train" split of the dataset