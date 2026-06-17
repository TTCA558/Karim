"""
DNS Cache Cleaner Module
Flushes the Windows DNS resolver cache to clear stale entries.
"""

import subprocess

def flush_dns(log_callback=None):
    """Flush the Windows DNS resolver cache (ipconfig /flushdns)."""
    try:
        if log_callback:
            log_callback("🌐 Flushing DNS cache...")
        
        result = subprocess.run(
            ['ipconfig', '/flushdns'],
            capture_output=True, text=True, timeout=30
        )
        
        if result.returncode == 0:
            if log_callback:
                log_callback("  ✓ DNS cache flushed successfully")
            return True
        else:
            if log_callback:
                log_callback(f"  ✗ DNS flush failed: {result.stderr}")
            return False
    except subprocess.TimeoutExpired:
        if log_callback:
            log_callback("  ✗ DNS flush timed out")
        return False
    except Exception as e:
        if log_callback:
            log_callback(f"  ✗ DNS flush error: {str(e)}")
        return False

def reset_winsock(log_callback=None):
    """Reset Winsock catalog to clean state (netsh winsock reset)."""
    try:
        if log_callback:
            log_callback("🔧 Resetting Winsock catalog...")
        
        result = subprocess.run(
            ['netsh', 'winsock', 'reset'],
            capture_output=True, text=True, timeout=30
        )
        
        if result.returncode == 0:
            if log_callback:
                log_callback("  ✓ Winsock reset successful")
            return True
        else:
            return False
    except Exception as e:
        if log_callback:
            log_callback(f"  ✗ Winsock reset error: {str(e)}")
        return False

def reset_ip_config(log_callback=None):
    """Release and renew IP configuration."""
    try:
        if log_callback:
            log_callback("🔄 Refreshing IP configuration...")
        
        subprocess.run(['ipconfig', '/release'],
            capture_output=True, text=True, timeout=30)
        
        if log_callback:
            log_callback("  → IP released, renewing...")
        
        result = subprocess.run(['ipconfig', '/renew'],
            capture_output=True, text=True, timeout=60)
        
        if result.returncode == 0:
            if log_callback:
                log_callback("  ✓ IP configuration renewed")
            return True
        return False
    except Exception as e:
        if log_callback:
            log_callback(f"  ✗ IP refresh error: {str(e)}")
        return False