"""
Script to export each record from the "Kaballas/SAP_NEW" Hugging Face dataset 
field "research_report" into its own .txt file using the "Title" field as the file name.
"""
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
    # Remove or replace invalid file name characters on Windows
    # Characters to avoid: \ / * ? " < > | and : (Windows-specific)
    sanitized = re.sub(r'[\\/*?\"<>|:]', '_', title)
    # Limit to 100 characters to ensure OS compatibility
    return sanitized[:100]

def export_dataset_to_txt():
    """
    Main function to load the dataset and export each record to a text file.
    """
    try:
        # Load the dataset
        print("Loading dataset 'Kaballas/SAP_NEW'...")
        dataset = load_dataset("Kaballas/SAP_NEW", split="train")
        
        # Create a directory to store output files
        output_dir = "C:\\DTT\\synthetic-data-kit\\data\\report"
        os.makedirs(output_dir, exist_ok=True)
        print(f"Output directory '{output_dir}' created or already exists.")
        
        # Get total number of records
        total_records = len(dataset)
        print(f"Dataset loaded successfully. Total records: {total_records}")
        
        # Check if required columns exist
        required_columns = ["Title", "research_report"]
        available_columns = dataset.column_names
        print(f"Available columns in dataset: {available_columns}")
        
        for col in required_columns:
            if col not in available_columns:
                raise ValueError(f"Required column '{col}' not found in dataset. Available columns: {available_columns}")
        
        # Counter for successful exports
        success_count = 0
        error_count = 0
        
        print(f"Starting export process...")
        for idx, record in enumerate(dataset, 1):
            try:
                title = sanitize_filename(record["Title"])
                
                # Handle empty or None titles
                if not title or title.isspace():
                    title = f"untitled_record_{idx}"
                
                # Get the content
                content = record["research_report"]
                
                # Create file path
                file_path = os.path.join(output_dir, f"{title}.txt")
                
                # Handle potential duplicate filenames by adding a suffix
                counter = 1
                original_file_path = file_path
                original_file_path_exists = os.path.exists(file_path)
                while os.path.exists(file_path):
                    name, ext = os.path.splitext(original_file_path)
                    file_path = f"{name}_{counter}{ext}"
                    counter += 1
                
                # Only report duplicate handling if it was actually needed
                if original_file_path_exists:
                    print(f"  Duplicate filename detected, using: {os.path.basename(file_path)}")
                
                # Write content to file, handling potential encoding issues
                # First, clean the content to ensure it doesn't have problematic characters
                clean_content = content.encode('utf-8', errors='replace').decode('utf-8')
                
                try:
                    with open(file_path, "w", encoding="utf-8") as f:
                        f.write(clean_content)
                except Exception as e:
                    print(f"Error writing file {file_path}: {e}")
                    error_count += 1
                    continue
                
                success_count += 1
                
                # Print progress every 10 records
                if idx % 10 == 0:
                    print(f"Processed {idx}/{total_records} records...")
                    
            except Exception as e:
                print(f"Error processing record {idx}: {e}")
                error_count += 1
        
        print(f"\nExport completed!")
        print(f"Successfully exported: {success_count} files")
        print(f"Errors encountered: {error_count}")
        print(f"Output directory: {output_dir}")
        
    except Exception as e:
        print(f"An error occurred while processing the dataset: {e}")

if __name__ == "__main__":
    export_dataset_to_txt()