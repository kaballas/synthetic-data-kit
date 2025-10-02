"""Script to verify that the combined JSONL file has valid JSON on each line."""
import json
from pathlib import Path

def verify_jsonl_file(file_path):
    """Verify that each line in a JSONL file is valid JSON."""
    file_path = Path(file_path)
    
    if not file_path.exists():
        print(f"File does not exist: {file_path}")
        return False
    
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    print(f"Verifying {len(lines)} lines in {file_path.name}...")
    
    valid_count = 0
    invalid_count = 0
    invalid_lines = []
    
    for i, line in enumerate(lines):
        line = line.strip()
        if not line:  # Skip empty lines
            continue
        try:
            json_obj = json.loads(line)
            valid_count += 1
        except json.JSONDecodeError as e:
            print(f"Invalid JSON on line {i+1}: {e}")
            print(f"  Content: {line[:100]}...")
            invalid_count += 1
            invalid_lines.append((i+1, line))
    
    print(f"\nVerification Results:")
    print(f"  Valid JSON lines: {valid_count}")
    print(f"  Invalid JSON lines: {invalid_count}")
    
    if invalid_count == 0:
        print("  All lines contain valid JSON")
        return True
    else:
        print("  Some lines contain invalid JSON")
        return False

if __name__ == "__main__":
    file_path = r"C:\DTT\synthetic-data-kit\data\generated\combined.jsonl"
    verify_jsonl_file(file_path)