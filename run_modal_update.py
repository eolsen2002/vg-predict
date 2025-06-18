# utils/run_modal_update.py
# Created: 6/17/25
# Backs up full_cycles files and runs modal day updater

from backup_full_cycles import backup_full_cycles
from scripts.update_modal_days import update_all_modal_days

if __name__ == "__main__":
    print("📦 Backing up full_cycles files...")
    backup_full_cycles()

    print("🔄 Updating modal day values...")
    update_all_modal_days()

    print("✅ Done.")
