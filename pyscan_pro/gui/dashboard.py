import customtkinter as ctk
import threading
import time
from gui.components import CTkScrollableTable
from core.scanner import Scanner
from core.reporter import Reporter
from tkinter import messagebox

class PyScanDashboard(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        
        self.scanner = Scanner(threads=150)
        self.scan_results = []
        self.start_time = 0
        
        self.setup_ui()
        
    def setup_ui(self):
        # Configure layout
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1) # The table weight
        
        # --- TOP HEADER PANEL ---
        self.header_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.header_frame.grid(row=0, column=0, padx=20, pady=20, sticky="ew")
        
        self.title_label = ctk.CTkLabel(self.header_frame, text="PyScan Pro", font=("Roboto", 28, "bold"), text_color="#1f6aa5")
        self.title_label.pack(side="left")
        
        self.timer_label = ctk.CTkLabel(self.header_frame, text="Elapsed Time: 00:00:00", font=("Roboto", 14))
        self.timer_label.pack(side="right", padx=10)
        
        # --- CONTROLS PANEL ---
        self.controls_frame = ctk.CTkFrame(self)
        self.controls_frame.grid(row=1, column=0, padx=20, pady=(0, 20), sticky="ew")
        self.controls_frame.grid_columnconfigure((0,1,2,3,4), weight=1)
        
        # Target Input
        self.target_entry = ctk.CTkEntry(self.controls_frame, placeholder_text="Target (e.g., 192.168.1.1, scanme.nmap.org)", width=300)
        self.target_entry.grid(row=0, column=0, padx=10, pady=15, sticky="ew")
        
        # Port Range Input
        self.port_entry = ctk.CTkEntry(self.controls_frame, placeholder_text="Ports (e.g., 80,443 or 1-1000)", width=200)
        self.port_entry.grid(row=0, column=1, padx=10, pady=15, sticky="ew")
        
        # Scan Type Dropdown
        self.scan_type_var = ctk.StringVar(value="tcp")
        self.scan_type_menu = ctk.CTkOptionMenu(
            self.controls_frame, 
            values=["tcp", "syn", "fast"],
            variable=self.scan_type_var,
            width=120
        )
        self.scan_type_menu.grid(row=0, column=2, padx=10, pady=15)
        
        # Action Buttons
        self.btn_start = ctk.CTkButton(self.controls_frame, text="Start Scan", command=self.start_scan, fg_color="#1f6aa5", text_color="white", hover_color="#144870")
        self.btn_start.grid(row=0, column=3, padx=10, pady=15)
        
        self.btn_stop = ctk.CTkButton(self.controls_frame, text="Stop", command=self.stop_scan, fg_color="#e74c3c", hover_color="#c0392b", state="disabled")
        self.btn_stop.grid(row=0, column=4, padx=10, pady=15)
        
        # --- RESULTS TABLE PANEL ---
        self.table = CTkScrollableTable(self, columns=["IP", "PORT", "STATUS", "SERVICE", "BANNER"])
        self.table.grid(row=2, column=0, padx=20, pady=(0, 20), sticky="nsew")
        
        # --- BOTTOM STATUS PANEL ---
        self.status_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.status_frame.grid(row=3, column=0, padx=20, pady=(0, 20), sticky="ew")
        self.status_frame.grid_columnconfigure(0, weight=1)
        
        self.progress_bar = ctk.CTkProgressBar(self.status_frame)
        self.progress_bar.grid(row=0, column=0, sticky="ew", padx=(0, 10))
        self.progress_bar.set(0)
        
        self.status_label = ctk.CTkLabel(self.status_frame, text="Ready", font=("Roboto", 12))
        self.status_label.grid(row=1, column=0, sticky="w", pady=(5, 0))
        
        self.export_btn = ctk.CTkButton(self.status_frame, text="Export JSON", command=self.export_report, width=100)
        self.export_btn.grid(row=0, column=1, rowspan=2, sticky="e")
        
    def start_scan(self):
        target = self.target_entry.get().strip()
        ports = self.port_entry.get().strip()
        scan_type = self.scan_type_var.get()
        
        if not target or not ports:
            messagebox.showwarning("Input Error", "Please provide both Target and Ports.")
            return
            
        # Reset UI
        self.table.clear()
        self.scan_results.clear()
        self.progress_bar.set(0)
        self.btn_start.configure(state="disabled")
        self.btn_stop.configure(state="normal")
        self.start_time = time.time()
        self.update_timer()
        
        # Start thread
        threading.Thread(target=self.scanner.start_scan, args=(
            target, ports, scan_type, self._update_progress, self._add_result
        ), daemon=True).start()
        
    def stop_scan(self):
        self.scanner.stop_scan()
        self.status_label.configure(text="Stopping scan...")
        self.btn_stop.configure(state="disabled")
        
    def export_report(self):
        if not self.scan_results:
            messagebox.showinfo("Export", "No results to export.")
            return
            
        target = self.target_entry.get().strip()
        reporter = Reporter(target, "json", self.scan_results)
        filepath = reporter.generate()
        messagebox.showinfo("Export Success", f"Report saved at:\n{filepath}")

    def _update_progress(self, current, total, status_text):
        if total > 0:
            progress = current / total
            # Safely update GUI from thread
            self.after(0, self.progress_bar.set, progress)
            self.after(0, self.status_label.configure, text=f"{status_text} | {current}/{total} Ports")
            
        if current >= total or not self.scanner.is_running:
            self.after(0, self.btn_start.configure, state="normal")
            self.after(0, self.btn_stop.configure, state="disabled")
            
    def _add_result(self, result: dict):
        self.scan_results.append(result)
        row_data = [result['ip'], result['port'], result['status'], result['service'], result.get('banner', 'N/A')[:30]]
        self.after(0, self.table.insert_row, row_data)
        
    def update_timer(self):
        if self.scanner.is_running:
            elapsed = int(time.time() - self.start_time)
            mins, secs = divmod(elapsed, 60)
            hours, mins = divmod(mins, 60)
            time_str = f"Elapsed Time: {hours:02d}:{mins:02d}:{secs:02d}"
            self.timer_label.configure(text=time_str)
            self.after(1000, self.update_timer)
