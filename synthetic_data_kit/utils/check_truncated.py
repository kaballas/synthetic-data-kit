import os

files = [f for f in os.listdir('research_reports_txt') if f.startswith('New Purge Request Type') or f.startswith('Payroll Control Center')]
for f in files:
    print(f'File: {f}')
    # Print the first 100 characters of the file to see its content
    filepath = os.path.join('research_reports_txt', f)
    print(f'  File path: {filepath}')
    print(f'  File size: {os.path.getsize(filepath)} bytes')
    with open(filepath, 'r', encoding='utf-8') as file:
        content = file.read(200)  # Read first 200 chars
        print(f'  Content starts with: {content[:50]}...')
        print()