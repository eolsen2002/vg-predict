# utils/debug.py
debug_mode = False

def debug_print(*args, **kwargs):
    if debug_mode:
        print("[DEBUG]", *args, **kwargs)
