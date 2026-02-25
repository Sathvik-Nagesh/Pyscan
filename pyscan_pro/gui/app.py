import customtkinter as ctk
from gui.dashboard import PyScanDashboard
from tkinter import messagebox
import sys

class PyScanApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        self.title("PyScan Pro - Advanced Network Scanner")
        self.geometry("1000x700")
        
        # Set modern dark theme
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue") # Set to professional blue instead of green
        
        self.show_disclaimer()
        
        self.dashboard = PyScanDashboard(self)
        self.dashboard.pack(fill="both", expand=True)
        
    def show_disclaimer(self):
        """Displays the ethical use disclaimer before using the tool."""
        msg = (
            "⚠️ ETHICAL USE DISCLAIMER ⚠️\n\n"
            "PyScan Pro is an educational tool designed to demonstrate networking, "
            "sockets, packet behavior, and security concepts.\n\n"
            "You MUST ONLY use this tool on systems and networks you own or "
            "have explicit, written permission to test.\n"
            "Unauthorized scanning may be illegal.\n\n"
            "Do you agree to use this tool responsibly?"
        )
        response = messagebox.askyesno("Ethical Use Agreement", msg)
        if not response:
            print("User declined ethical agreement. Exiting.")
            sys.exit(0)

def run_gui():
    app = PyScanApp()
    app.mainloop()
