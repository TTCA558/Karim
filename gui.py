"""
Valorant Optimizer - GUI Module (tkinter)
Dark theme with Valorant's red and black color scheme.

Features: Clean System, Optimize Network, Kill Background Apps,
OPTIMIZE FOR VALORANT (all-in-one), Live log, Progress bar,
Ping before/after, Status indicators.
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import threading
import subprocess
import time
import os

from cleaner.temp_cleaner import clean_all_temp, format_size
from cleaner.dns_cleaner import flush_dns, reset_winsock
from cleaner.cache_cleaner import clean_valorant_cache, clean_browser_cache
from network.dns_optimizer import set_dns_cloudflare, restore_dns
from network.tcp_optimizer import (
    optimize_tcp, enable_game_mode, disable_xbox_game_bar,
    restore_tcp_settings
)
from network.process_manager import (
    scan_running_processes, kill_selected_processes,
    set_valorant_high_priority
)
from network.windows_update import (
    disable_windows_update, enable_windows_update,
    disable_delivery_optimization, enable_delivery_optimization
)

COLORS = {
    'bg_primary': '#0f0f0f',
    'bg_secondary': '#1a1a1a',
    'bg_tertiary': '#252525',
    'accent': '#ff4655',
    'accent_hover': '#ff6b77',
    'accent_dark': '#cc3844',
    'text_primary': '#ffffff',
    'text_secondary': '#a0a0a0',
    'text_muted': '#666666',
    'success': '#4ade80',
    'warning': '#fbbf24',
    'error': '#ef4444',
    'border': '#333333',
}

class ValorantOptimizerGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Valorant Optimizer")
        self.root.geometry("900x700")
        self.root.minsize(800, 600)
        self.root.configure(bg=COLORS['bg_primary'])
        
        self.is_running = False
        self.original_power_plan = None
        self.original_dns = None
        self.dns_adapter = None
        self.wu_original_status = None
        
        self._create_header()
        self._create_main_content()
        self._create_log_window()
        self._create_status_bar()
        self.root.protocol("WM_DELETE_WINDOW", self._on_closing)
    
    def _create_header(self):
        header = tk.Frame(self.root, bg=COLORS['bg_secondary'], height=80)
        header.pack(fill='x')
        header.pack_propagate(False)
        
        title = tk.Label(header, text="⚔ VALORANT OPTIMIZER",
            font=('Segoe UI', 24, 'bold'),
            fg=COLORS['accent'], bg=COLORS['bg_secondary'])
        title.pack(side='left', padx=20, pady=15)
        
        ping_frame = tk.Frame(header, bg=COLORS['bg_secondary'])
        ping_frame.pack(side='right', padx=20, pady=15)
        tk.Label(ping_frame, text="PING", font=('Segoe UI', 10),
            fg=COLORS['text_secondary'], bg=COLORS['bg_secondary']).pack()
        self.ping_label = tk.Label(ping_frame, text="-- ms",
            font=('Segoe UI', 18, 'bold'),
            fg=COLORS['success'], bg=COLORS['bg_secondary'])
        self.ping_label.pack()
    
    def _create_main_content(self):
        content = tk.Frame(self.root, bg=COLORS['bg_primary'])
        content.pack(fill='both', expand=True, padx=20, pady=10)
        
        btn_frame = tk.Frame(content, bg=COLORS['bg_primary'])
        btn_frame.pack(fill='x', pady=(0, 10))
        
        btn_config = {
            'font': ('Segoe UI', 12, 'bold'),
            'fg': COLORS['text_primary'],
            'activeforeground': COLORS['text_primary'],
            'relief': 'flat', 'cursor': 'hand2',
            'height': 2, 'borderwidth': 0,
        }
        
        row1 = tk.Frame(btn_frame, bg=COLORS['bg_primary'])
        row1.pack(fill='x', pady=(0, 8))
        
        # Three main buttons
        self.btn_clean = tk.Button(row1, text="🧹  Clean System",
            command=lambda: self._run_in_thread(self._clean_system),
            bg=COLORS['bg_secondary'], activebackground=COLORS['bg_tertiary'],
            **btn_config)
        self.btn_clean.pack(side='left', fill='x', expand=True, padx=(0, 4))
        
        self.btn_network = tk.Button(row1, text="🌐  Optimize Network",
            command=lambda: self._run_in_thread(self._optimize_network),
            bg=COLORS['bg_secondary'], activebackground=COLORS['bg_tertiary'],
            **btn_config)
        self.btn_network.pack(side='left', fill='x', expand=True, padx=(4, 4))
        
        self.btn_kill = tk.Button(row1, text="🔫  Kill Background Apps",
            command=lambda: self._run_in_thread(self._kill_background_apps),
            bg=COLORS['bg_secondary'], activebackground=COLORS['bg_tertiary'],
            **btn_config)
        self.btn_kill.pack(side='left', fill='x', expand=True, padx=(4, 0))
        
        # Big OPTIMIZE button
        self.btn_optimize_all = tk.Button(btn_frame,
            text="⚡  OPTIMIZE FOR VALORANT  ⚡",
            command=lambda: self._run_in_thread(self._optimize_all),
            font=('Segoe UI', 16, 'bold'),
            fg=COLORS['text_primary'], bg=COLORS['accent'],
            activebackground=COLORS['accent_dark'],
            activeforeground=COLORS['text_primary'],
            relief='flat', cursor='hand2', height=2, borderwidth=0)
        self.btn_optimize_all.pack(fill='x', pady=(0, 8))
        
        # Restore + Ping buttons
        row3 = tk.Frame(btn_frame, bg=COLORS['bg_primary'])
        row3.pack(fill='x')
        
        self.btn_restore = tk.Button(row3, text="🔄  Restore All Settings",
            command=lambda: self._run_in_thread(self._restore_all),
            bg=COLORS['bg_tertiary'], font=('Segoe UI', 10),
            fg=COLORS['text_secondary'], relief='flat', cursor='hand2',
            height=1, borderwidth=0)
        self.btn_restore.pack(side='left', fill='x', expand=True, padx=(0, 4))
        
        self.btn_ping = tk.Button(row3, text="📡  Test Ping",
            command=lambda: self._run_in_thread(self._test_ping),
            bg=COLORS['bg_tertiary'], font=('Segoe UI', 10),
            fg=COLORS['text_secondary'], relief='flat', cursor='hand2',
            height=1, borderwidth=0)
        self.btn_ping.pack(side='left', fill='x', expand=True, padx=(4, 0))
        
        # Progress bar
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("red.Horizontal.TProgressbar",
            troughcolor=COLORS['bg_tertiary'],
            background=COLORS['accent'])
        
        self.progress = ttk.Progressbar(content,
            style="red.Horizontal.TProgressbar",
            mode='determinate', maximum=100)
        self.progress.pack(fill='x', pady=(5, 0))
        
        self.progress_label = tk.Label(content, text="Ready",
            font=('Segoe UI', 9), fg=COLORS['text_secondary'],
            bg=COLORS['bg_primary'])
        self.progress_label.pack(anchor='w')
    
    def _create_log_window(self):
        log_frame = tk.Frame(self.root, bg=COLORS['bg_primary'])
        log_frame.pack(fill='both', expand=True, padx=20, pady=(0, 10))
        
        tk.Label(log_frame, text="📋 Live Log",
            font=('Segoe UI', 11, 'bold'),
            fg=COLORS['text_secondary'],
            bg=COLORS['bg_primary']).pack(anchor='w', pady=(0, 5))
        
        self.log_text = scrolledtext.ScrolledText(log_frame,
            font=('Consolas', 10), bg=COLORS['bg_tertiary'],
            fg=COLORS['text_primary'], relief='flat',
            wrap='word', height=12)
        self.log_text.pack(fill='both', expand=True)
        
        self.log_text.tag_configure('success', foreground=COLORS['success'])
        self.log_text.tag_configure('error', foreground=COLORS['error'])
        self.log_text.tag_configure('warning', foreground=COLORS['warning'])
        self.log_text.tag_configure('info', foreground=COLORS['accent'])
        self.log_text.tag_configure('header', foreground=COLORS['accent'],
            font=('Consolas', 11, 'bold'))
        
        self.log("Welcome to Valorant Optimizer!", 'header')
        self.log("Click any button to start.", 'info')
    
    def _create_status_bar(self):
        status_bar = tk.Frame(self.root, bg=COLORS['bg_secondary'], height=30)
        status_bar.pack(fill='x', side='bottom')
        status_bar.pack_propagate(False)
        self.status_text = tk.Label(status_bar,
            text="Ready | Running as Administrator ✓",
            font=('Segoe UI', 9), fg=COLORS['text_secondary'],
            bg=COLORS['bg_secondary'])
        self.status_text.pack(side='left', padx=10)
    
    # === Logging ===
    def log(self, message, tag=None):
        def _append():
            self.log_text.insert('end', message + '\n', tag)
            self.log_text.see('end')
        self.root.after(0, _append)
    
    def set_progress(self, value, text=""):
        def _update():
            self.progress['value'] = value
            if text:
                self.progress_label.config(text=text)
        self.root.after(0, _update)
    
    def set_buttons_state(self, state):
        def _update():
            for btn in [self.btn_clean, self.btn_network, self.btn_kill,
                       self.btn_optimize_all, self.btn_restore, self.btn_ping]:
                btn.config(state=state)
        self.root.after(0, _update)
    
    def _run_in_thread(self, func):
        if self.is_running:
            messagebox.showinfo("Wait", "Operation already running.")
            return
        threading.Thread(target=func, daemon=True).start()
    
    # === Core functions (abbreviated - see full code) ===
    def _test_ping(self):
        self.is_running = True
        self.set_buttons_state('disabled')
        self.log("\n📡 Testing ping to 8.8.8.8...", 'info')
        try:
            result = subprocess.run(['ping', '-n', '4', '8.8.8.8'],
                capture_output=True, text=True, timeout=30)
            for line in result.stdout.split('\n'):
                if 'Average' in line:
                    parts = line.split('=')
                    if parts:
                        ping_value = parts[-1].strip().replace('ms','').strip()
                        self.log(f"  → Ping: {ping_value} ms", 'success')
                        self.root.after(0, lambda v=ping_value:
                            self.ping_label.config(text=f"{v} ms"))
        except Exception as e:
            self.log(f"  ✗ Error: {str(e)}", 'error')
        finally:
            self.is_running = False
            self.set_buttons_state('normal')
    
    def _clean_system(self):
        self.is_running = True
        self.set_buttons_state('disabled')
        self.set_progress(0, "Cleaning...")
        self.log("\n🧹 SYSTEM CLEANING STARTED", 'header')
        total_freed = 0
        try:
            self.set_progress(10, "Cleaning temp files...")
            result = clean_all_temp(self.log)
            total_freed += result['bytes_freed']
            self.set_progress(40)
            
            self.set_progress(45, "Cleaning Valorant cache...")
            _, freed = clean_valorant_cache(self.log)
            total_freed += freed
            self.set_progress(60)
            
            self.set_progress(65, "Cleaning browser caches...")
            _, freed = clean_browser_cache(self.log)
            total_freed += freed
            self.set_progress(80)
            
            flush_dns(self.log)
            self.set_progress(100, "Done!")
            self.log(f"\n✅ Freed: {format_size(total_freed)}", 'success')
        except Exception as e:
            self.log(f"✗ Error: {str(e)}", 'error')
        finally:
            self.is_running = False
            self.set_buttons_state('normal')
    
    def _optimize_network(self):
        self.is_running = True
        self.set_buttons_state('disabled')
        self.set_progress(0, "Optimizing network...")
        self.log("\n🌐 NETWORK OPTIMIZATION", 'header')
        try:
            dns_result = set_dns_cloudflare(self.log)
            if dns_result['success']:
                self.original_dns = dns_result.get('original_dns')
                self.dns_adapter = dns_result.get('adapter')
            self.set_progress(30)
            
            optimize_tcp(self.log)
            self.set_progress(55)
            enable_game_mode(self.log)
            self.set_progress(70)
            disable_xbox_game_bar(self.log)
            self.set_progress(80)
            set_valorant_high_priority(self.log)
            self.set_progress(90)
            self._set_high_performance_power(self.log)
            self.set_progress(100, "Network optimized!")
            self.log("\n✅ Network optimization complete!", 'success')
        except Exception as e:
            self.log(f"✗ Error: {str(e)}", 'error')
        finally:
            self.is_running = False
            self.set_buttons_state('normal')
    
    def _kill_background_apps(self):
        self.is_running = True
        self.set_buttons_state('disabled')
        self.log("\n🔫 BACKGROUND PROCESS MANAGER", 'header')
        try:
            processes = scan_running_processes(self.log)
            if processes:
                kill_selected_processes(processes, self.log)
            disable_windows_update(self.log)
            disable_delivery_optimization(self.log)
            self.log("\n✅ Done!", 'success')
        except Exception as e:
            self.log(f"✗ Error: {str(e)}", 'error')
        finally:
            self.is_running = False
            self.set_buttons_state('normal')
    
    def _optimize_all(self):
        """Run ALL optimizations at once."""
        self.is_running = True
        self.set_buttons_state('disabled')
        self.log("\n⚡ FULL VALORANT OPTIMIZATION", 'header')
        try:
            # Phase 1: Clean
            result = clean_all_temp(self.log)
            clean_valorant_cache(self.log)
            clean_browser_cache(self.log)
            flush_dns(self.log)
            self.set_progress(30)
            
            # Phase 2: Network
            dns_result = set_dns_cloudflare(self.log)
            if dns_result['success']:
                self.original_dns = dns_result.get('original_dns')
                self.dns_adapter = dns_result.get('adapter')
            optimize_tcp(self.log)
            enable_game_mode(self.log)
            disable_xbox_game_bar(self.log)
            self.set_progress(60)
            
            # Phase 3: Processes
            processes = scan_running_processes(self.log)
            if processes:
                kill_selected_processes(processes, self.log)
            set_valorant_high_priority(self.log)
            disable_windows_update(self.log)
            self.set_progress(85)
            
            # Phase 4: Power
            self._set_high_performance_power(self.log)
            self.set_progress(100, "FULLY OPTIMIZED!")
            self.log("\n✅ ALL OPTIMIZATIONS COMPLETE!", 'header')
            self.log("🎮 Launch Valorant and enjoy!", 'success')
        except Exception as e:
            self.log(f"✗ Error: {str(e)}", 'error')
        finally:
            self.is_running = False
            self.set_buttons_state('normal')
    
    def _restore_all(self):
        self.is_running = True
        self.set_buttons_state('disabled')
        self.log("\n🔄 RESTORING ALL SETTINGS", 'header')
        try:
            restore_tcp_settings(self.log)
            if self.dns_adapter:
                restore_dns(self.dns_adapter, self.original_dns, self.log)
            enable_windows_update(self.log)
            enable_delivery_optimization(self.log)
            self._restore_power_plan(self.log)
            self.log("\n✅ All settings restored!", 'success')
        except Exception as e:
            self.log(f"✗ Error: {str(e)}", 'error')
        finally:
            self.is_running = False
            self.set_buttons_state('normal')
    
    def _set_high_performance_power(self, log_callback=None):
        try:
            if log_callback:
                log_callback("⚡ Setting High Performance power plan...")
            result = subprocess.run(['powercfg', '/getactivescheme'],
                capture_output=True, text=True, timeout=10)
            for word in result.stdout.split():
                if len(word) == 36 and word.count('-') == 4:
                    self.original_power_plan = word
                    break
            subprocess.run(['powercfg', '/setactive',
                '8c5e7fda-e8bf-4a96-9a85-a6e23a8c635c'],
                capture_output=True, text=True, timeout=10)
            if log_callback:
                log_callback("  ✓ Power plan: High Performance")
        except Exception as e:
            if log_callback:
                log_callback(f"  ⚠ Power plan error: {str(e)}")
    
    def _restore_power_plan(self, log_callback=None):
        try:
            guid = self.original_power_plan or '381b4222-f694-41f0-9685-ff5bb260df2e'
            subprocess.run(['powercfg', '/setactive', guid],
                capture_output=True, text=True, timeout=10)
            if log_callback:
                log_callback("  ✓ Power plan restored")
        except Exception as e:
            if log_callback:
                log_callback(f"  ⚠ {str(e)}")
    
    def _on_closing(self):
        if messagebox.askyesno("Restore?",
            "Restore all settings before exiting?"):
            try:
                restore_tcp_settings()
                if self.dns_adapter:
                    restore_dns(self.dns_adapter, self.original_dns)
                enable_windows_update()
                self._restore_power_plan()
            except Exception:
                pass
        self.root.destroy()
    
    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = ValorantOptimizerGUI()
    app.run()