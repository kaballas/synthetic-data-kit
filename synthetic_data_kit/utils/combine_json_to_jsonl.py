"""
Script to combine all .json files in a directory into a single .jsonl file.

JSONL (JSON Lines) format is a text format where each line is a separate JSON object.
This is useful for streaming large datasets or for certain data processing applications.
"""
import json
import os
from pathlib import Path

def combine_json_files_to_jsonl(input_directory, output_file):
    """
    Combines all .json files in the input directory into a single .jsonl file.
    
    Args:
        input_directory (str): Path to the directory containing .json files
        output_file (str): Path to the output .jsonl file
    """
    input_path = Path(input_directory)
    
    # Verify input directory exists
    if not input_path.exists():
        raise FileNotFoundError(f"Input directory does not exist: {input_directory}")
    
    if not input_path.is_dir():
        raise NotADirectoryError(f"Input path is not a directory: {input_directory}")
    
    # Find all .json files in the directory
    json_files = list(input_path.glob("*.json"))
    
    if not json_files:
        print(f"No .json files found in directory: {input_directory}")
        return
    
    print(f"Found {len(json_files)} .json files to process:")
    for file in json_files:
        print(f"  - {file.name}")
    
    # Write to the output file in JSONL format
    with open(output_file, 'w', encoding='utf-8') as outfile:
        processed_count = 0
        error_count = 0
        
        for json_file in json_files:
            try:
                with open(json_file, 'r', encoding='utf-8') as infile:
                    # Try to parse the JSON file
                    content = json.load(infile)
                    
                    # If the JSON content is a single object, write it as a line
                    if isinstance(content, dict):
                        json_line = json.dumps(content, ensure_ascii=False)
                        outfile.write(json_line + '\n')
                        processed_count += 1
                    # If the JSON content is an array, write each element as a separate line
                    elif isinstance(content, list):
                        for item in content:
                            json_line = json.dumps(item, ensure_ascii=False)
                            outfile.write(json_line + '\n')
                            processed_count += 1
                    else:
                        print(f"Warning: Unsupported JSON structure in {json_file.name}, skipping...")
                        continue
            except json.JSONDecodeError as e:
                print(f"Error: Invalid JSON in file {json_file.name}: {e}")
                error_count += 1
            except Exception as e:
                print(f"Error processing file {json_file.name}: {e}")
                error_count += 1
        
        print(f"\nProcessing complete!")
        print(f"  - Successfully processed: {processed_count} JSON objects")
        print(f"  - Errors encountered: {error_count}")
        print(f"  - Output file: {output_file}")

def main():
    """Main function to run the JSON to JSONL converter."""
    input_directory = r"C:\DTT\synthetic-data-kit\data\generated\done"
    output_file = r"C:\DTT\synthetic-data-kit\data\generated\combined.jsonl"
    
    print("JSON to JSONL Converter")
    print("=" * 50)
    print(f"Input directory: {input_directory}")
    print(f"Output file: {output_file}")
    print()
    
    try:
        combine_json_files_to_jsonl(input_directory, output_file)
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()