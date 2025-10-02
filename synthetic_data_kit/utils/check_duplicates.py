from datasets import load_dataset

dataset = load_dataset('Kaballas/SAP_NEW', split='train')
titles = [record['Title'] for record in dataset]
print(f'Total records: {len(titles)}')
print(f'Unique titles: {len(set(titles))}')

# Count occurrences of each title
from collections import Counter
title_counts = Counter(titles)

# Find titles that appear more than once
duplicates = {title: count for title, count in title_counts.items() if count > 1}
print(f'Duplicate titles: {len(duplicates)}')
if duplicates:
    for title, count in duplicates.items():
        print(f'  \"{title}\" appears {count} times')