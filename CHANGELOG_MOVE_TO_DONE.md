# Feature: Auto-move Processed Files to Done Folder

## Overview
Added functionality to automatically move successfully processed files to a `done/` subfolder after processing completes. This helps:
- Keep track of which files have been processed
- Avoid accidentally reprocessing files
- Organize your input directories
- Maintain a clean workflow

## How It Works

When you run any directory processing command, files that are successfully processed will automatically be moved to a `done/` subfolder within the same directory:

```
data/input/
├── file1.txt          # Before processing
├── file2.txt
└── file3.txt

# After processing:

data/input/
├── done/
│   ├── file1.txt      # Successfully processed files moved here
│   ├── file2.txt
│   └── file3.txt
```

## Affected Commands

This feature applies to all directory processing commands:

1. **`synthetic-data-kit ingest ./data/input/`**
   - Moves processed PDFs, HTML, DOCX, etc. to `./data/input/done/`

2. **`synthetic-data-kit create ./data/input/ --type cot`**
   - Moves processed .txt files to `./data/input/done/`

3. **`synthetic-data-kit curate ./data/generated/`**
   - Moves processed .json files to `./data/generated/done/`

4. **`synthetic-data-kit save-as ./data/curated/ --format alpaca`**
   - Moves processed .json files to `./data/curated/done/`

## Behavior Details

- **Only successful files are moved**: Files that fail processing remain in the original directory
- **Automatic folder creation**: The `done/` subfolder is created automatically if it doesn't exist
- **Duplicate handling**: If a file with the same name already exists in `done/`, a number suffix is added (e.g., `file_1.txt`, `file_2.txt`)
- **Verbose mode**: Use `-v` flag to see detailed messages about file movements

## Example Usage

### Process CoT examples and auto-organize:
```bash
synthetic-data-kit create ./data/input/ --type cot --num-pairs 20 -v
```

Output:
```
✓ A Time Range Is Required for Proxy Assignments.txt
  → Moved to done/A Time Range Is Required for Proxy Assignments.txt
✓ Add New Employee To This Position.txt
  → Moved to done/Add New Employee To This Position.txt
...
```

### Rerun on same directory (only unprocessed files):
```bash
# Files in done/ subfolder are not scanned, so you can safely rerun
synthetic-data-kit create ./data/input/ --type cot --num-pairs 20
```

## Restore Files (if needed)

If you need to reprocess files, simply move them back:

```bash
# Move all files back to input directory
Move-Item ./data/input/done/*.txt ./data/input/

# Or move specific files
Move-Item ./data/input/done/specific-file.txt ./data/input/
```

## Technical Implementation

- Location: `synthetic_data_kit/utils/directory_processor.py`
- Function: `move_to_done_folder(file_path, verbose)`
- Uses: `shutil.move()` for atomic file operations
- Integrated into: All directory processing functions

## Future Enhancements

Potential improvements:
- Add `--no-move` flag to disable this behavior
- Add `--move-failed` flag to also move failed files to a `failed/` subfolder
- Add timestamp subdirectories for better organization (e.g., `done/2025-10-02/`)
- Add ability to configure custom destination folder
