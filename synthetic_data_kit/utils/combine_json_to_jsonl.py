"""
Incrementally append JSON objects from .json files into an existing .jsonl file.

Rules:
- Do NOT create a new JSONL. If the JSONL does not exist, fail fast.
- Maintain a sidecar manifest (output_file + ".manifest.json") that tracks processed files and mtimes.
- Only append content from new or modified .json files.
- Robustly parse .json, arrays, objects, and fallback to line-by-line JSONL parsing.
"""

import json
import os
from pathlib import Path
from typing import Dict, Tuple

def _load_manifest(manifest_path: Path) -> Dict[str, float]:
    if manifest_path.exists():
        try:
            with open(manifest_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            # Expect {"processed_files": {"abs_path": mtime_float}}
            return data.get("processed_files", {})
        except Exception:
            # Corrupt manifest -> start fresh
            return {}
    return {}

def _save_manifest(manifest_path: Path, processed_files: Dict[str, float]) -> None:
    tmp_path = manifest_path.with_suffix(manifest_path.suffix + ".tmp")
    with open(tmp_path, "w", encoding="utf-8") as f:
        json.dump({"processed_files": processed_files}, f, ensure_ascii=False, indent=2)
    os.replace(tmp_path, manifest_path)

def _process_json_file_to_out(in_path: Path, out_handle) -> Tuple[int, int]:
    """
    Return (processed_count, error_count) for a single input file.
    """
    processed = 0
    errors = 0
    try:
        with open(in_path, "r", encoding="utf-8") as infile:
            try:
                content = json.load(infile)
            except json.JSONDecodeError as e:
                print(f"Warning: Standard JSON decode failed for {in_path.name}: {e}")
                infile.seek(0)
                line_no = 0
                for line in infile:
                    line_no += 1
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        obj = json.loads(line)
                        out_handle.write(json.dumps(obj, ensure_ascii=False) + "\n")
                        processed += 1
                    except Exception as le:
                        print(f"Error: Invalid JSON object in {in_path.name} (line {line_no}): {le}")
                        errors += 1
                if processed > 0:
                    print(f"  - Processed {processed} JSON objects from lines in {in_path.name}")
                return processed, errors

            # Parsed as standard JSON
            if isinstance(content, dict):
                out_handle.write(json.dumps(content, ensure_ascii=False) + "\n")
                processed += 1
            elif isinstance(content, list):
                for item in content:
                    out_handle.write(json.dumps(item, ensure_ascii=False) + "\n")
                    processed += 1
            else:
                print(f"Warning: Unsupported JSON structure in {in_path.name}, skipping...")
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in file {in_path.name}: {e}")
        errors += 1
    except Exception as e:
        print(f"Error processing file {in_path.name}: {e}")
        errors += 1

    return processed, errors

def combine_json_files_to_existing_jsonl(input_directory: str, output_file: str):
    """
    Incrementally appends JSON objects from .json files in input_directory
    into an EXISTING output .jsonl file.

    Preconditions:
      - output_file MUST already exist; otherwise, raise FileNotFoundError.
    """
    input_path = Path(input_directory)
    output_path = Path(output_file)

    # Guards
    if not input_path.exists():
        raise FileNotFoundError(f"Input directory does not exist: {input_directory}")
    if not input_path.is_dir():
        raise NotADirectoryError(f"Input path is not a directory: {input_directory}")
    if not output_path.exists():
        raise FileNotFoundError(
            f"Output .jsonl does not exist (creation is disallowed): {output_file}"
        )
    if output_path.is_dir():
        raise IsADirectoryError(f"Output path is a directory, expected file: {output_file}")

    manifest_path = output_path.with_suffix(output_path.suffix + ".manifest.json")
    processed_index = _load_manifest(manifest_path)

    # Gather .json files deterministically
    json_files = sorted(input_path.glob("*.jsonl"))
    if not json_files:
        print(f"No .json files found in directory: {input_directory}")
        return

    print(f"Found {len(json_files)} .json files to evaluate:")
    for f in json_files:
        print(f"  - {f.name}")

    # Work
    total_appended = 0
    total_errors = 0
    total_skipped = 0

    # Open output strictly in append mode; never truncate.
    with open(output_path, "a", encoding="utf-8") as outfile:
        for idx, jf in enumerate(json_files, 1):
            abs_path = str(jf.resolve())
            mtime = jf.stat().st_mtime

            already = abs_path in processed_index
            unchanged = already and processed_index.get(abs_path) == mtime

            if unchanged:
                total_skipped += 1
                print(f"[SKIP] {idx}/{len(json_files)}: {jf.name} (unchanged)")
                continue

            # If file is seen but modified, reprocess; if unseen, process.
            state = "modified" if already else "new"
            print(f"[APPEND:{state}] {idx}/{len(json_files)}: {jf.name}")

            processed, errors = _process_json_file_to_out(jf, outfile)
            total_appended += processed
            total_errors += errors

            # Only mark as processed if we wrote at least one object and had no fatal errors reading file object structure.
            # If nothing processed and errors > 0, still update mtime to avoid reattempt loops; you can delete manifest to retry.
            processed_index[abs_path] = mtime

    # Persist manifest (atomic replace)
    _save_manifest(manifest_path, processed_index)

    print("\nUpdate complete.")
    print(f"  - Appended objects: {total_appended}")
    print(f"  - Files skipped (unchanged): {total_skipped}")
    print(f"  - Errors encountered: {total_errors}")
    print(f"  - Output file (unchanged path): {output_file}")
    print(f"  - Manifest: {manifest_path}")

def main():
    """Main entrypoint for incremental JSON -> existing JSONL updater."""
    input_directory = r"C:\DTT\synthetic-data-kit\data\final"
    output_file = r"C:\DTT\synthetic-data-kit\data\tv\combined.jsonl"

    print("Incremental JSON -> JSONL Updater (No new JSONL creation)")
    print("=" * 60)
    print(f"Input directory: {input_directory}")
    print(f"Output file:     {output_file}\n")

    try:
        combine_json_files_to_existing_jsonl(input_directory, output_file)
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
