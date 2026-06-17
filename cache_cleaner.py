"""
Cache Cleaner Module
Cleans Valorant game cache and browser caches.
"""

import os
import shutil

def clean_valorant_cache(log_callback=None):
    """Clean Valorant game cache files at %LocalAppData%\\VALORANT\\Saved\\"""
    files_deleted = 0
    bytes_freed = 0
    
    valorant_path = os.path.join(
        os.environ.get('LOCALAPPDATA', ''),
        'VALORANT', 'Saved'
    )
    
    if not os.path.exists(valorant_path):
        if log_callback:
            log_callback("  ⚠ Valorant cache folder not found")
        return files_deleted, bytes_freed
    
    if log_callback:
        log_callback("🎮 Cleaning Valorant cache...")
    
    for folder in ['webcache', 'Logs', 'Crashes']:
        folder_path = os.path.join(valorant_path, folder)
        if os.path.exists(folder_path):
            try:
                size = get_dir_size(folder_path)
                shutil.rmtree(folder_path, ignore_errors=True)
                if not os.path.exists(folder_path):
                    files_deleted += 1
                    bytes_freed += size
                    if log_callback:
                        log_callback(f"  ✓ Deleted: {folder} ({format_size(size)})")
            except Exception as e:
                if log_callback:
                    log_callback(f"  ⚠ Could not clean {folder}")
    
    return files_deleted, bytes_freed

def clean_browser_cache(log_callback=None):
    """Clean browser caches for Chrome, Firefox, and Edge."""
    total_files = 0
    total_bytes = 0
    
    local_app = os.environ.get('LOCALAPPDATA', '')
    
    browsers = {
        'Chrome': [
            os.path.join(local_app, 'Google', 'Chrome', 'User Data', 'Default', 'Cache'),
            os.path.join(local_app, 'Google', 'Chrome', 'User Data', 'Default', 'Code Cache'),
        ],
        'Edge': [
            os.path.join(local_app, 'Microsoft', 'Edge', 'User Data', 'Default', 'Cache'),
        ],
        'Firefox': [
            os.path.join(local_app, 'Mozilla', 'Firefox', 'Profiles'),
        ]
    }
    
    for browser_name, paths in browsers.items():
        if log_callback:
            log_callback(f"🌐 Cleaning {browser_name} cache...")
        
        browser_freed = 0
        for path in paths:
            if not os.path.exists(path):
                continue
            try:
                for item in os.listdir(path):
                    item_path = os.path.join(path, item)
                    try:
                        if os.path.isfile(item_path):
                            file_size = os.path.getsize(item_path)
                            os.remove(item_path)
                            total_files += 1
                            total_bytes += file_size
                            browser_freed += file_size
                        elif os.path.isdir(item_path):
                            dir_size = get_dir_size(item_path)
                            shutil.rmtree(item_path, ignore_errors=True)
                            total_files += 1
                            total_bytes += dir_size
                            browser_freed += dir_size
                    except (PermissionError, OSError):
                        pass
            except Exception:
                pass
        
        if log_callback:
            log_callback(f"  → {browser_name}: {format_size(browser_freed)} freed")
    
    return total_files, total_bytes

def get_dir_size(path):
    """Calculate total size of a directory."""
    total = 0
    try:
        for dirpath, dirnames, filenames in os.walk(path):
            for f in filenames:
                try:
                    total += os.path.getsize(os.path.join(dirpath, f))
                except (OSError, PermissionError):
                    pass
    except (OSError, PermissionError):
        pass
    return total

def format_size(bytes_count):
    """Convert bytes to human-readable format."""
    if bytes_count < 1024:
        return f"{bytes_count} B"
    elif bytes_count < 1024 * 1024:
        return f"{bytes_count / 1024:.1f} KB"
    elif bytes_count < 1024 * 1024 * 1024:
        return f"{bytes_count / (1024 * 1024):.1f} MB"
    else:
        return f"{bytes_count / (1024 * 1024 * 1024):.2f} GB"