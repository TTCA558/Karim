"""
DNS Optimizer Module
Changes DNS to Cloudflare (1.1.1.1 / 1.0.0.1) for lowest latency.
"""

import subprocess
import winreg

CLOUDFLARE_PRIMARY = "1.1.1.1"
CLOUDFLARE_SECONDARY = "1.0.0.1"

def get_active_adapter(log_callback=None):
    """Get the name of the active network adapter."""
    try:
        result = subprocess.run(
            ['netsh', 'interface', 'show', 'interface'],
            capture_output=True, text=True, timeout=10
        )
        
        for line in result.stdout.split('\n'):
            if 'Connected' in line and 'Dedicated' not in line:
                parts = line.split()
                if len(parts) >= 4:
                    adapter_name = ' '.join(parts[3:])
                    if log_callback:
                        log_callback(f"  → Found adapter: {adapter_name}")
                    return adapter_name
        return None
    except Exception as e:
        if log_callback:
            log_callback(f"  ✗ Error finding adapter: {str(e)}")
        return None

def get_current_dns(adapter_name, log_callback=None):
    """Get the current DNS settings for backup."""
    try:
        result = subprocess.run(
            ['netsh', 'interface', 'ip', 'show', 'dns', adapter_name],
            capture_output=True, text=True, timeout=10
        )
        dns_servers = []
        for line in result.stdout.split('\n'):
            parts = line.strip().split()
            for part in parts:
                if part.count('.') == 3 and all(
                    p.isdigit() and 0 <= int(p) <= 255
                    for p in part.split('.')
                ):
                    dns_servers.append(part)
        if dns_servers:
            return {
                'primary': dns_servers[0],
                'secondary': dns_servers[1] if len(dns_servers) > 1 else None
            }
        return None
    except Exception:
        return None

def set_dns_cloudflare(log_callback=None):
    """Change DNS to Cloudflare 1.1.1.1 / 1.0.0.1"""
    if log_callback:
        log_callback("🌐 Optimizing DNS settings...")
    
    adapter = get_active_adapter(log_callback)
    if not adapter:
        return {'success': False, 'error': 'No active adapter found'}
    
    original_dns = get_current_dns(adapter, log_callback)
    
    try:
        # Set primary DNS
        subprocess.run(
            ['netsh', 'interface', 'ip', 'set', 'dns',
             adapter, 'static', CLOUDFLARE_PRIMARY, 'primary'],
            capture_output=True, text=True, timeout=10
        )
        if log_callback:
            log_callback(f"  ✓ Primary DNS set to {CLOUDFLARE_PRIMARY}")
        
        # Set secondary DNS
        subprocess.run(
            ['netsh', 'interface', 'ip', 'add', 'dns',
             adapter, CLOUDFLARE_SECONDARY, 'index=2'],
            capture_output=True, text=True, timeout=10
        )
        if log_callback:
            log_callback(f"  ✓ Secondary DNS set to {CLOUDFLARE_SECONDARY}")
        
        return {
            'success': True,
            'original_dns': original_dns,
            'adapter': adapter
        }
    except Exception as e:
        return {'success': False, 'error': str(e)}

def restore_dns(adapter, original_dns=None, log_callback=None):
    """Restore DNS settings to original values or DHCP."""
    try:
        if original_dns and original_dns.get('primary'):
            subprocess.run(
                ['netsh', 'interface', 'ip', 'set', 'dns',
                 adapter, 'static', original_dns['primary'], 'primary'],
                capture_output=True, text=True, timeout=10
            )
        else:
            subprocess.run(
                ['netsh', 'interface', 'ip', 'set', 'dns',
                 adapter, 'dhcp'],
                capture_output=True, text=True, timeout=10
            )
        if log_callback:
            log_callback("  ✓ DNS restored")
        return True
    except Exception as e:
        if log_callback:
            log_callback(f"  ✗ Error restoring DNS: {str(e)}")
        return False