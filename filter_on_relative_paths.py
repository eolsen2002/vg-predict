# filter_on_relative_paths.py

input_file = 'file_list_relative.txt'
output_file = 'filtered_files.txt'

filtered = []
for line in open(input_file, 'r'):
    line = line.strip()
    # Exclude venv folder completely
    if line.startswith('venv\\'):
        continue

    # Include all files in these folders (including dotfiles)
    if (
        line.startswith('data\\') or
        line.startswith('signals\\') or
        line.startswith('analysis\\') or
        line.startswith('scripts\\') or
        line.startswith('reports\\')  # <-- include all reports files, including dotfiles
    ):
        filtered.append(line)
        continue

    # Include root README.md and .gitignore
    if line in ('README.md', '.gitignore'):
        filtered.append(line)
        continue

    # Include root level .py or .csv files only (no subfolders)
    if ('\\' not in line) and (line.endswith('.py') or line.endswith('.csv')):
        filtered.append(line)

with open(output_file, 'w') as f:
    for item in filtered:
        f.write(item + '\n')

print(f"Filtered {len(filtered)} files written to {output_file}")
