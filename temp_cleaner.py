"""
Temp Cleaner Module - Handles cleaning of temporary files
Cleans: %TEMP%, Windows\\Temp, Prefetch, and Thumbnail cache.
"""

import os
import shutil
import glob

def get_temp_paths():
    """Get all temporary file paths that can be safely cleaned."""
    user_temp = os.environ.get('TEMP', os.path.join(os.environ['USERPROFILE'], 'AppData', 'Local', 'Temp'))
    paths = {
        'User Temp': user_temp,
        'Windows Temp': r'C:\\Windows\\Temp',
        'Prefetch': r'C:\\Windows\\Prefetch',
        'Thumbnail Cache': os.path.join(
            os.environ.get('LOCALAPPDATA', ''),
            'Microsoft', 'Windows', 'Explorer'
        )
    }
    return paths

def clean_directory(path, log_callback=None):
    """Clean all files and folders in the given directory."""
    files_deleted = 0
    bytes_freed = 0
    errors = 0
    
    if not os.path.exists(path):
        if log_callback:
            log_callback(f"  ⚠ Path does not exist: {path}")
        return files_deleted, bytes_freed, errors
    
    for item in os.listdir(path):
        item_path = os.path.join(path, item)
        try:
            if os.path.isfile(item_path):
                file_size = os.path.getsize(item_path)
                os.remove(item_path)
                files_deleted += 1
                bytes_freed += file_size
            elif os.path.isdir(item_path):
                dir_size = get_directory_size(item_path)
                shutil.rmtree(item_path, ignore_errors=True)
                if not os.path.exists(item_path):
                    files_deleted += 1
                    bytes_freed += dir_size
                else:
                    errors += 1
        except PermissionError:
            errors += 1
            if log_callback:
                log_callback(f"  ⚠ Skipped (in use): {item}")
        except Exception as e:
            errors += 1
    
    return files_deleted, bytes_freed, errors

def get_directory_size(path):
    """Calculate the total size of a directory in bytes."""
    total_size = 0
    try:
        for dirpath, dirnames, filenames in os.walk(path):
            for filename in filenames:
                filepath = os.path.join(dirpath, filename)
                try:
                    total_size += os.path.getsize(filepath)
                except (OSError, PermissionError):
                    pass
    except (OSError, PermissionError):
        pass
    return total_size

def clean_thumbnail_cache(log_callback=None):
    """Clean Windows thumbnail cache files (thumbcache_*.db)."""
    cache_path = os.path.join(
        os.environ.get('LOCALAPPDATA', ''),
        'Microsoft', 'Windows', 'Explorer'
    )
    files_deleted = 0
    bytes_freed = 0
    
    if not os.path.exists(cache_path):
        return files_deleted, bytes_freed
    
    for pattern in ['thumbcache_*.db', 'iconcache_*.db']:
        for filepath in glob.glob(os.path.join(cache_path, pattern)):
            try:
                size = os.path.getsize(filepath)
                os.remove(filepath)
                files_deleted += 1
                bytes_freed += size
            except (PermissionError, OSError):
                pass
    
    return files_deleted, bytes_freed

def clean_all_temp(log_callback=None):
    """Master function to clean all temporary files."""
    total_files = 0
    total_bytes = 0
    total_errors = 0
    
    paths = get_temp_paths()
    
    for name, path in paths.items():
        if log_callback:
            log_callback(f"🧹 Cleaning {name}...")
        
        if name == 'Thumbnail Cache':
            files, freed = clean_thumbnail_cache(log_callback)
            total_files += files
            total_bytes += freed
        else:
            files, freed, errors = clean_directory(path, log_callback)
            total_files += files
            total_bytes += freed
            total_errors += errors
        
        if log_callback:
            log_callback(f"  → {name}: {files} items, {format_size(freed)} freed")
    
    return {
        'files_deleted': total_files,
        'bytes_freed': total_bytes,
        'errors': total_errors
    }

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