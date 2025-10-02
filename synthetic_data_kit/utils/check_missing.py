from datasets import load_dataset
import os
import re

def sanitize_filename(title):
    """
    Sanitize the title to make it a valid file name by removing or replacing invalid characters.
    
    Args:
        title (str): The input title string that may contain invalid file name characters
    
    Returns:
        str: A sanitized filename safe for file system operations
    """
    # Remove or replace invalid file name characters
    # Characters to avoid: \ / * ? " < > |
    sanitized = re.sub(r'[\\/*?\"<>|]', '_', title)
    # Limit to 100 characters to ensure OS compatibility
    return sanitized[:100]

def check_missing_files():
    """
    Check to see which files might be missing from the export process.
    """
    # Load the dataset
    print("Loading dataset 'Kaballas/SAP_NEW'...")
    dataset = load_dataset("Kaballas/SAP_NEW", split="train")
    
    # Get all titles
    titles = [record["Title"] for record in dataset]
    
    # Sanitize all titles
    sanitized_titles = [sanitize_filename(title) for title in titles]
    
    # Check output directory
    output_dir = "research_reports_txt"
    if not os.path.exists(output_dir):
        print(f"Output directory {output_dir} does not exist!")
        return
    
    # Get all .txt files in output directory
    output_files = [f for f in os.listdir(output_dir) if f.endswith('.txt')]
    # Remove the .txt extension to get just the filenames
    output_basenames = [os.path.splitext(f)[0] for f in output_files]
    
    print(f"Total records in dataset: {len(titles)}")
    print(f"Total unique titles: {len(set(sanitized_titles))}")
    print(f"Total files in output directory: {len(output_files)}")
    
    # Find what titles are missing from the output
    missing_from_output = []
    for i, sanitized_title in enumerate(sanitized_titles):
        # Check if this sanitized title exists as a file (with or without counter suffixes like _1, _2, etc.)
        found = False
        for output_basename in output_basenames:
            if output_basename.startswith(sanitized_title) and (output_basename == sanitized_title or 
               output_basename.startswith(sanitized_title + "_")):
                found = True
                break
        
        if not found:
            missing_from_output.append((i, titles[i], sanitized_title))
    
    if missing_from_output:
        print(f"\nMissing {len(missing_from_output)} records from output:")
        for idx, original_title, sanitized_title in missing_from_output:
            print(f"  {idx}: \"{original_title}\" (sanitized: \"{sanitized_title}\")")
    else:
        print("\nAll records have corresponding output files!")
    
    # Also check for potential duplicates in the output
    from collections import Counter
    basename_counts = Counter(output_basenames)
    duplicates_in_output = {basename: count for basename, count in basename_counts.items() if count > 1}
    
    if duplicates_in_output:
        print(f"\nDuplicate output files found:")
        for basename, count in duplicates_in_output.items():
            print(f"  {basename}.txt appears {count} times")

if __name__ == "__main__":
    check_missing_files()