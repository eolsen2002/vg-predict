# remove_full_absolute_prefix.py

input_file = 'file_list.txt'
output_file = 'file_list_relative.txt'
root_path = 'C:\\xampp\\htdocs\\vg-predict\\'  # EXACT match prefix including trailing backslash

matched_count = 0
total_count = 0

with open(input_file, 'r') as f_in, open(output_file, 'w') as f_out:
    for line in f_in:
        total_count += 1
        line = line.strip()
        if line.lower().startswith(root_path.lower()):
            matched_count += 1
            rel_path = line[len(root_path):]
            f_out.write(rel_path + '\n')

print(f"Total lines: {total_count}")
print(f"Lines matched root_path: {matched_count}")
