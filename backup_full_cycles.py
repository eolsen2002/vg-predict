# backup_full_cycles.py
"""
Here’s a simple Python script snippet you can run before your batch updates that:

Finds all *_full_cycles.csv files in your signals folder

Copies them to a backup folder with a timestamp suffix so you can restore if needed
"""
import os
import shutil
from datetime import datetime

def backup_full_cycles(source_dir='signals', backup_dir='backup_full_cycles'):
    if not os.path.exists(backup_dir):
        os.makedirs(backup_dir)
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backed_up_files = []

    for filename in os.listdir(source_dir):
        if filename.endswith('_full_cycles.csv'):
            src_path = os.path.join(source_dir, filename)
            backup_filename = f"{filename.replace('.csv', '')}_{timestamp}.csv"
            backup_path = os.path.join(backup_dir, backup_filename)
            shutil.copy2(src_path, backup_path)
            backed_up_files.append(backup_filename)

    print(f"Backed up {len(backed_up_files)} files to {backup_dir}:")
    for f in backed_up_files:
        print(f"  - {f}")

if __name__ == "__main__":
    backup_full_cycles()
