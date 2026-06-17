"""
TCP Optimizer Module
Applies TCP/IP registry tweaks to reduce network latency and jitter.
Disables Nagle's Algorithm for immediate packet sending.
"""

import winreg
import json
import os

TCP_PARAMS_PATH = r"SYSTEM\\CurrentControlSet\\Services\\Tcpip\\Parameters"
TCP_INTERFACES_PATH = r"SYSTEM\\CurrentControlSet\\Services\\Tcpip\\Parameters\\Interfaces"

TCP_TWEAKS = {
    'TcpAckFrequency': 1,    # ACK every packet immediately
    'TCPNoDelay': 1,          # Disable Nagle's algorithm
    'TcpDelAckTicks': 0,      # No delay on ACK packets
}

BACKUP_FILE = os.path.join(
    os.environ.get('APPDATA', ''),
    'ValorantOptimizer', 'tcp_backup.json'
)

def save_backup(original_values):
    """Save original registry values for later restoration."""
    try:
        backup_dir = os.path.dirname(BACKUP_FILE)
        if not os.path.exists(backup_dir):
            os.makedirs(backup_dir)
        with open(BACKUP_FILE, 'w') as f:
            json.dump(original_values, f, indent=2)
        return True
    except Exception:
        return False

def load_backup():
    """Load original registry values from backup."""
    try:
        if os.path.exists(BACKUP_FILE):
            with open(BACKUP_FILE, 'r') as f:
                return json.load(f)
    except Exception:
        pass
    return None

def get_registry_value(key_path, value_name, hive=winreg.HKEY_LOCAL_MACHINE):
    """Read a value from the Windows Registry."""
    try:
        key = winreg.OpenKey(hive, key_path, 0, winreg.KEY_READ)
        value, reg_type = winreg.QueryValueEx(key, value_name)
        winreg.CloseKey(key)
        return value
    except FileNotFoundError:
        return None

def set_registry_value(key_path, value_name, value_data,
                       value_type=winreg.REG_DWORD,
                       hive=winreg.HKEY_LOCAL_MACHINE):
    """Write a value to the Windows Registry."""
    try:
        key = winreg.OpenKey(hive, key_path, 0, winreg.KEY_SET_VALUE)
        winreg.SetValueEx(key, value_name, 0, value_type, value_data)
        winreg.CloseKey(key)
        return True
    except FileNotFoundError:
        try:
            key = winreg.CreateKey(hive, key_path)
            winreg.SetValueEx(key, value_name, 0, value_type, value_data)
            winreg.CloseKey(key)
            return True
        except Exception:
            return False
    except Exception:
        return False

def optimize_tcp(log_callback=None):
    """Apply all TCP optimization tweaks for gaming."""
    if log_callback:
        log_callback("⚡ Optimizing TCP/IP settings...")
    
    original_values = {}
    tweaks_applied = 0
    errors = []
    
    # Read and backup current values
    for name, new_value in TCP_TWEAKS.items():
        current = get_registry_value(TCP_PARAMS_PATH, name)
        original_values[name] = current
        if log_callback:
            log_callback(f"  → {name}: {current} → {new_value}")
    
    save_backup(original_values)
    
    # Apply TCP tweaks
    for name, value in TCP_TWEAKS.items():
        try:
            success = set_registry_value(TCP_PARAMS_PATH, name, value)
            if success:
                tweaks_applied += 1
                if log_callback:
                    log_callback(f"  ✓ {name} = {value}")
            else:
                errors.append(f"Failed to set {name}")
        except Exception as e:
            errors.append(f"{name}: {str(e)}")
    
    # Disable Nagle's on all interfaces
    nagle_count = disable_nagle_all_interfaces(log_callback)
    tweaks_applied += nagle_count
    
    return {'success': len(errors) == 0, 'tweaks_applied': tweaks_applied, 'errors': errors}

def disable_nagle_all_interfaces(log_callback=None):
    """Disable Nagle's Algorithm on ALL network interfaces."""
    count = 0
    try:
        if log_callback:
            log_callback("  🔧 Disabling Nagle's Algorithm...")
        
        interfaces_key = winreg.OpenKey(
            winreg.HKEY_LOCAL_MACHINE, TCP_INTERFACES_PATH, 0, winreg.KEY_READ
        )
        
        i = 0
        while True:
            try:
                interface_id = winreg.EnumKey(interfaces_key, i)
                interface_path = f"{TCP_INTERFACES_PATH}\\{interface_id}"
                set_registry_value(interface_path, 'TcpAckFrequency', 1)
                set_registry_value(interface_path, 'TCPNoDelay', 1)
                count += 1
                i += 1
            except OSError:
                break
        
        winreg.CloseKey(interfaces_key)
        if log_callback:
            log_callback(f"  ✓ Nagle disabled on {count} interfaces")
    except Exception as e:
        if log_callback:
            log_callback(f"  ⚠ Nagle error: {str(e)}")
    return count

def enable_game_mode(log_callback=None):
    """Enable Windows Game Mode via Registry."""
    try:
        if log_callback:
            log_callback("🎮 Enabling Windows Game Mode...")
        success = set_registry_value(
            r"Software\\Microsoft\\GameBar", 'AutoGameModeEnabled', 1,
            hive=winreg.HKEY_CURRENT_USER
        )
        if success and log_callback:
            log_callback("  ✓ Game Mode enabled")
        return success
    except Exception as e:
        if log_callback:
            log_callback(f"  ✗ Game Mode error: {str(e)}")
        return False

def disable_xbox_game_bar(log_callback=None):
    """Disable Xbox Game Bar overlay to reduce CPU usage."""
    try:
        if log_callback:
            log_callback("🎮 Disabling Xbox Game Bar...")
        success = set_registry_value(
            r"SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\GameDVR",
            'AppCaptureEnabled', 0,
            hive=winreg.HKEY_CURRENT_USER
        )
        if success and log_callback:
            log_callback("  ✓ Xbox Game Bar disabled")
        return success
    except Exception as e:
        if log_callback:
            log_callback(f"  ✗ Game Bar error: {str(e)}")
        return False

def restore_tcp_settings(log_callback=None):
    """Restore all TCP settings to original values from backup."""
    if log_callback:
        log_callback("🔄 Restoring TCP settings...")
    
    backup = load_backup()
    if not backup:
        if log_callback:
            log_callback("  ⚠ No backup found")
        return False
    
    for name, original_value in backup.items():
        try:
            if original_value is not None:
                set_registry_value(TCP_PARAMS_PATH, name, original_value)
                if log_callback:
                    log_callback(f"  ✓ Restored {name} = {original_value}")
            else:
                try:
                    key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE,
                        TCP_PARAMS_PATH, 0, winreg.KEY_SET_VALUE)
                    winreg.DeleteValue(key, name)
                    winreg.CloseKey(key)
                except FileNotFoundError:
                    pass
        except Exception as e:
            if log_callback:
                log_callback(f"  ⚠ Could not restore {name}")
    return True