"""
Process Manager Module
Detects and kills background processes that consume bandwidth.
Sets Valorant process priority to HIGH.
"""

import psutil

BANDWIDTH_HOGS = {
    'OneDrive.exe': 'Microsoft OneDrive (cloud sync)',
    'Dropbox.exe': 'Dropbox (cloud sync)',
    'GoogleDriveFS.exe': 'Google Drive (cloud sync)',
    'MicrosoftEdgeUpdate.exe': 'Edge auto-updater',
    'steam.exe': 'Steam client',
    'steamwebhelper.exe': 'Steam web helper',
    'EpicWebHelper.exe': 'Epic Games web helper',
    'Spotify.exe': 'Spotify (streaming music)',
    'Teams.exe': 'Microsoft Teams',
    'Slack.exe': 'Slack',
}

PROTECTED_PROCESSES = {
    'System', 'smss.exe', 'csrss.exe', 'wininit.exe',
    'services.exe', 'lsass.exe', 'svchost.exe', 'dwm.exe',
    'explorer.exe', 'VALORANT.exe',
    'VALORANT-Win64-Shipping.exe', 'RiotClientServices.exe',
    'vgc.exe', 'vgtray.exe',
}

def scan_running_processes(log_callback=None):
    """Scan for bandwidth-heavy background processes."""
    found_processes = []
    
    if log_callback:
        log_callback("🔍 Scanning for bandwidth-heavy processes...")
    
    try:
        for proc in psutil.process_iter(['pid', 'name', 'memory_info']):
            try:
                proc_name = proc.info['name']
                if proc_name in BANDWIDTH_HOGS:
                    memory_mb = proc.info['memory_info'].rss / (1024 * 1024)
                    found_processes.append({
                        'pid': proc.info['pid'],
                        'name': proc_name,
                        'description': BANDWIDTH_HOGS[proc_name],
                        'memory_mb': round(memory_mb, 1)
                    })
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
    except Exception as e:
        if log_callback:
            log_callback(f"  ✗ Error: {str(e)}")
    
    if log_callback:
        log_callback(f"  → Found {len(found_processes)} processes")
    return found_processes

def kill_process(pid, process_name, log_callback=None):
    """Kill a specific process by PID."""
    if process_name in PROTECTED_PROCESSES:
        if log_callback:
            log_callback(f"  ⚠ PROTECTED: {process_name}")
        return False
    
    try:
        process = psutil.Process(pid)
        process.terminate()
        try:
            process.wait(timeout=5)
        except psutil.TimeoutExpired:
            process.kill()
        if log_callback:
            log_callback(f"  ✓ Killed: {process_name} (PID: {pid})")
        return True
    except psutil.NoSuchProcess:
        return True
    except psutil.AccessDenied:
        if log_callback:
            log_callback(f"  ✗ Access denied: {process_name}")
        return False
    except Exception as e:
        if log_callback:
            log_callback(f"  ✗ Error: {str(e)}")
        return False

def kill_selected_processes(process_list, log_callback=None):
    """Kill a list of processes."""
    killed = 0
    failed = 0
    memory_freed = 0.0
    
    if log_callback:
        log_callback(f"🔫 Killing {len(process_list)} processes...")
    
    for proc in process_list:
        success = kill_process(proc['pid'], proc['name'], log_callback)
        if success:
            killed += 1
            memory_freed += proc.get('memory_mb', 0)
        else:
            failed += 1
    
    if log_callback:
        log_callback(f"  → Killed: {killed}, Failed: {failed}")
        log_callback(f"  → Memory freed: ~{memory_freed:.0f} MB")
    
    return {'killed': killed, 'failed': failed, 'memory_freed_mb': memory_freed}

def set_valorant_high_priority(log_callback=None):
    """Set Valorant's process priority to HIGH."""
    valorant_names = ['VALORANT-Win64-Shipping.exe', 'VALORANT.exe']
    found = False
    
    if log_callback:
        log_callback("⚡ Setting Valorant to HIGH priority...")
    
    try:
        for proc in psutil.process_iter(['pid', 'name']):
            try:
                if proc.info['name'] in valorant_names:
                    proc.nice(psutil.HIGH_PRIORITY_CLASS)
                    found = True
                    if log_callback:
                        log_callback(f"  ✓ {proc.info['name']} set to HIGH priority")
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
    except Exception as e:
        if log_callback:
            log_callback(f"  ✗ Error: {str(e)}")
    
    if not found and log_callback:
        log_callback("  ⚠ Valorant is not running")
    return found