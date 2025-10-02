# Check content of a previously problematic file
try:
    with open('research_reports_txt/New Purge Request Type_ DRTM Delegation Purge.txt', 'r', encoding='utf-8') as f:
        content = f.read(200)
        print('File content starts with:', repr(content))
        print('File size:', len(f.read()) + 200, 'bytes (after rewinding)')
except FileNotFoundError:
    print('File not found')
except Exception as e:
    print(f'Error reading file: {e}')

# Also check the other one
try:
    with open('research_reports_txt/Payroll Control Center_ Manage Payroll Activities.txt', 'r', encoding='utf-8') as f:
        content = f.read(200)
        print('Payroll file content starts with:', repr(content))
except FileNotFoundError:
    print('Payroll file not found')
except Exception as e:
    print(f'Error reading payroll file: {e}')