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
    print(f"[DEBUG] Original title: {title} | Sanitized filename: {sanitized[:100]}")
    # Limit to 100 characters to ensure OS compatibility
    return sanitized[:100]

def export_dataset_to_txt():
    """
    Main function to load the dataset and export each record to a text file.
    """
    try:
        print("[DEBUG] Starting dataset export function.")
        # Load the dataset
        print("Loading dataset 'Kaballas/chatgpt07'...")
        dataset = load_dataset("Kaballas/chatgpt07", split="train")
        print(f"[DEBUG] Dataset object type: {type(dataset)}")
        print(f"[DEBUG] First record sample: {dataset[0] if len(dataset) > 0 else 'Dataset empty'}")
        
        # Create a directory to store output files
        output_dir = "C:\\DTT\\synthetic-data-kit\\data\\report"
        print(f"[DEBUG] Output directory to be used: {output_dir}")
        os.makedirs(output_dir, exist_ok=True)
        print(f"Output directory '{output_dir}' created or already exists.")
        
        # Get total number of records
        total_records = len(dataset)
        print(f"Dataset loaded successfully. Total records: {total_records}")
        
        # Check if required columns exist
        required_columns = ["title", "messages"]
        available_columns = dataset.column_names
        print(f"Available columns in dataset: {available_columns}")
        print(f"[DEBUG] Required columns: {required_columns}")
        
        for col in required_columns:
            if col not in available_columns:
                print(f"[DEBUG] Missing required column: {col}")
                raise ValueError(f"Required column '{col}' not found in dataset. Available columns: {available_columns}")
        
        # Counter for successful exports
        success_count = 0
        error_count = 0
        
        print(f"Starting export process...")
        for idx, record in enumerate(dataset, 1):
            print(f"[DEBUG] Processing record {idx}/{total_records}")
            try:
                title = record["title"]
                print(f"[DEBUG] Raw title: {title}")
                sanitized_title = sanitize_filename(title)
                print(f"[DEBUG] Sanitized title: {sanitized_title}")
                
                # Get the content
                content = record["messages"] 
                print(f"[DEBUG] Content type: {type(content)} | Content preview: {str(content)[:100]}")
                
                # Convert list of messages to string if needed
                if isinstance(content, list):
                    # Join messages as text, e.g., each message on a new line with role/content
                    content_str = "\n".join(
                        f"[{msg.get('role', 'unknown')}] {msg.get('content', '')}" for msg in content
                    )
                    print(f"[DEBUG] Converted messages list to string. Preview: {content_str[:100]}")
                else:
                    content_str = str(content)
                
                # Create file path
                file_path = os.path.join(output_dir, f"{sanitized_title}.txt")
                print(f"[DEBUG] Initial file path: {file_path}")
                
                # Handle potential duplicate filenames by adding a suffix
                counter = 1
                original_file_path = file_path
                original_file_path_exists = os.path.exists(file_path)
                while os.path.exists(file_path):
                    print(f"[DEBUG] File path exists: {file_path}")
                    name, ext = os.path.splitext(original_file_path)
                    file_path = f"{name}_{counter}{ext}"
                    print(f"[DEBUG] Trying new file path: {file_path}")
                    counter += 1
                
                # Only report duplicate handling if it was actually needed
                if original_file_path_exists:
                    print(f"  Duplicate filename detected, using: {os.path.basename(file_path)}")
                
                # Write content to file, handling potential encoding issues
                # First, clean the content to ensure it doesn't have problematic characters
                clean_content = content_str.encode('utf-8', errors='replace').decode('utf-8')
                print(f"[DEBUG] Cleaned content length: {len(clean_content)}")
                try:
                    with open(file_path, "w", encoding="utf-8") as f:
                        f.write(clean_content)
                    print(f"[DEBUG] Successfully wrote file: {file_path}")
                except Exception as e:
                    print(f"Error writing file {file_path}: {e}")
                    print(f"[DEBUG] Write error details: {e}")
                    error_count += 1
                    continue
                
                success_count += 1
                
                # Print progress every 10 records
                if idx % 10 == 0:
                    print(f"Processed {idx}/{total_records} records...")
                    
            except Exception as e:
                print(f"Error processing record {idx}: {e}")
                print(f"[DEBUG] Record error details: {e}")
                error_count += 1
        
        print(f"\nExport completed!")
        print(f"Successfully exported: {success_count} files")
        print(f"Errors encountered: {error_count}")
        print(f"Output directory: {output_dir}")
        print(f"[DEBUG] Export process finished.")
    except Exception as e:
        print(f"An error occurred while processing the dataset: {e}")
        print(f"[DEBUG] Top-level exception: {e}")

if __name__ == "__main__":
    print("[DEBUG] __main__ entrypoint reached.")
    export_dataset_to_txt()