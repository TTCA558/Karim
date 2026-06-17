"""
Windows Update Manager Module
Temporarily disables Windows Update to save bandwidth during gaming.
Re-enables on exit.
"""

import subprocess

def get_service_status(service_name, log_callback=None):
    """Get the current status of a Windows service."""
    try:
        result = subprocess.run(
            ['sc', 'query', service_name],
            capture_output=True, text=True, timeout=10
        )
        output = result.stdout
        if 'RUNNING' in output:
            return 'RUNNING'
        elif 'STOPPED' in output:
            return 'STOPPED'
        else:
            return 'UNKNOWN'
    except Exception as e:
        return f'ERROR: {str(e)}'

def disable_windows_update(log_callback=None):
    """Temporarily stop and disable Windows Update service."""
    service_name = 'wuauserv'
    
    if log_callback:
        log_callback("🔒 Disabling Windows Update temporarily...")
    
    original_status = get_service_status(service_name)
    
    if original_status == 'STOPPED':
        if log_callback:
            log_callback("  ✓ Windows Update is already stopped")
        return {'success': True, 'original_status': original_status}
    
    try:
        subprocess.run(['sc', 'stop', service_name],
            capture_output=True, text=True, timeout=30)
        if log_callback:
            log_callback("  ✓ Windows Update service stopped")
        
        subprocess.run(['sc', 'config', service_name, 'start=', 'disabled'],
            capture_output=True, text=True, timeout=10)
        if log_callback:
            log_callback("  ✓ Windows Update auto-start disabled")
        
        return {'success': True, 'original_status': original_status}
    except Exception as e:
        if log_callback:
            log_callback(f"  ✗ Error: {str(e)}")
        return {'success': False, 'original_status': original_status}

def enable_windows_update(log_callback=None):
    """Re-enable Windows Update service."""
    service_name = 'wuauserv'
    
    if log_callback:
        log_callback("🔓 Re-enabling Windows Update...")
    
    try:
        subprocess.run(['sc', 'config', service_name, 'start=', 'auto'],
            capture_output=True, text=True, timeout=10)
        subprocess.run(['sc', 'start', service_name],
            capture_output=True, text=True, timeout=30)
        if log_callback:
            log_callback("  ✓ Windows Update re-enabled")
        return True
    except Exception as e:
        if log_callback:
            log_callback(f"  ✗ Error: {str(e)}")
        return False

def disable_delivery_optimization(log_callback=None):
    """Disable Windows Delivery Optimization service."""
    try:
        if log_callback:
            log_callback("🔒 Disabling Delivery Optimization...")
        subprocess.run(['sc', 'stop', 'DoSvc'],
            capture_output=True, text=True, timeout=30)
        if log_callback:
            log_callback("  ✓ Delivery Optimization stopped")
        return True
    except Exception as e:
        if log_callback:
            log_callback(f"  ⚠ {str(e)}")
        return False

def enable_delivery_optimization(log_callback=None):
    """Re-enable Delivery Optimization."""
    try:
        subprocess.run(['sc', 'start', 'DoSvc'],
            capture_output=True, text=True, timeout=30)
        if log_callback:
            log_callback("  ✓ Delivery Optimization re-enabled")
        return True
    except Exception:
        return False