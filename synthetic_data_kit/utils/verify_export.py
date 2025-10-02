from datasets import load_dataset
import os
import re

def sanitize_filename(title):
    """
    Sanitize the title to make it a valid file name by removing or replacing invalid characters.
    """
    # Remove or replace invalid file name characters on Windows
    # Characters to avoid: \ / * ? " < > | and : (Windows-specific)
    sanitized = re.sub(r'[\\/*?\"<>|:]', '_', title)
    # Limit to 100 characters to ensure OS compatibility
    return sanitized[:100]

def verify_export():
    """
    Verify that all records were properly exported to files.
    """
    # Load the dataset
    print("Loading dataset 'Kaballas/SAP_NEW'...")
    dataset = load_dataset("Kaballas/SAP_NEW", split="train")
    
    # Get all titles and sanitize them
    original_titles = [record["Title"] for record in dataset]
    sanitized_titles = [sanitize_filename(title) for title in original_titles]
    
    # Check output directory
    output_dir = "research_reports_txt"
    if not os.path.exists(output_dir):
        print(f"Output directory {output_dir} does not exist!")
        return False
    
    # Get all .txt files in output directory
    output_files = [f for f in os.listdir(output_dir) if f.endswith('.txt')]
    output_basenames = [os.path.splitext(f)[0] for f in output_files]
    
    print(f"Total records in dataset: {len(original_titles)}")
    print(f"Total unique original titles: {len(set(original_titles))}")
    print(f"Total unique sanitized titles: {len(set(sanitized_titles))}")
    print(f"Total files in output directory: {len(output_files)}")
    
    # Check if all sanitized titles exist in the output
    missing_files = []
    extra_files = []
    
    # For each sanitized title, check if there's a corresponding file
    for i, sanitized_title in enumerate(sanitized_titles):
        found = False
        for output_basename in output_basenames:
            if output_basename.startswith(sanitized_title) and (output_basename == sanitized_title or 
               output_basename.startswith(sanitized_title + "_")):
                found = True
                break
        
        if not found:
            missing_files.append((i, original_titles[i], sanitized_title))
    
    # Check for any files that don't correspond to any record
    for output_basename in output_basenames:
        found = False
        for sanitized_title in sanitized_titles:
            if output_basename.startswith(sanitized_title) and (output_basename == sanitized_title or 
               output_basename.startswith(sanitized_title + "_")):
                found = True
                break
        
        if not found:
            extra_files.append(output_basename)
    
    print(f"\nVerification Results:")
    print(f"  Missing files: {len(missing_files)}")
    print(f"  Extra files: {len(extra_files)}")
    
    if missing_files:
        print(f"\nMissing files details:")
        for idx, original_title, sanitized_title in missing_files[:5]:  # Show first 5
            print(f"    Record {idx}: \"{original_title}\" -> sanitized to \"{sanitized_title}\"")
        if len(missing_files) > 5:
            print(f"    ... and {len(missing_files) - 5} more")
    
    if extra_files:
        print(f"\nExtra files (not corresponding to any record):")
        for f in extra_files[:5]:  # Show first 5
            print(f"    {f}")
        if len(extra_files) > 5:
            print(f"    ... and {len(extra_files) - 5} more")
    
    success = len(missing_files) == 0 and len(extra_files) == 0
    print(f"\nExport {'SUCCESSFUL' if success else 'FAILED'}")
    
    return success

if __name__ == "__main__":
    verify_export()