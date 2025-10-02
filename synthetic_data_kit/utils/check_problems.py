from datasets import load_dataset
import re
import os

dataset = load_dataset('Kaballas/SAP_NEW', split='train')

def sanitize_filename(title):
    if not title or title.isspace():
        return 'untitled_record'
    # Remove or replace invalid file name characters
    sanitized = re.sub(r'[\\/*?\"<>|]', '_', title)
    # Limit to 100 characters to ensure OS compatibility
    return sanitized[:100]

# Check all titles
all_titles = []
problematic_records = []
for i, record in enumerate(dataset):
    title = record['Title']
    all_titles.append(title)
    
    # Check if title is problematic
    if not title or title.isspace():
        problematic_records.append((i, title, "Empty or whitespace"))
    
    # Check if research_report content exists
    research_report = record['research_report']
    if not research_report or research_report.isspace():
        if (i, title, "Empty or whitespace") not in problematic_records:
            problematic_records.append((i, title, "Empty research_report"))

print(f'Total records: {len(dataset)}')
print(f'Total problematic records: {len(problematic_records)}')

if problematic_records:
    print('\nProblematic records:')
    for idx, title, issue in problematic_records:
        print(f'  {idx}: \"{title}\" - {issue}')
else:
    print('No problematic records found')

# Check if our output directory exists and count files
output_dir = "research_reports_txt"
if os.path.exists(output_dir):
    files = [f for f in os.listdir(output_dir) if f.endswith('.txt')]
    print(f'\nFiles in output directory: {len(files)}')
else:
    print(f'\nOutput directory {output_dir} does not exist')