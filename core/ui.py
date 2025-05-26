import tkinter as tk
from tkinter import ttk
import importlib
import os

APP_DIR = "apps"

class RonynDeskApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("RonynDesk")
        self.configure(bg="#111111")
        self.geometry("800x600")
        self.resizable(False, False)

        try:
            icon_path = os.path.join("assets", "icons", "samurai.ico")
            self.iconbitmap(icon_path)
        except Exception as e:
            print(f"Could not load icon: {e}")

        style = ttk.Style(self)
        style.theme_use("default")
        style.configure("TFrame", background="#111111")
        style.configure("TLabel", background="#111111", foreground="white")
        style.configure("TButton", background="#222222", foreground="white")

        self.container = ttk.Frame(self)
        self.container.pack(fill="both", expand=True, padx=20, pady=20)

        self.load_apps()

    def load_apps(self):
        app_buttons = []
        for app_name in os.listdir(APP_DIR):
            app_path = os.path.join(APP_DIR, app_name)
            if os.path.isdir(app_path) and "ui.py" in os.listdir(app_path):
                btn = ttk.Button(self.container, text=app_name.replace("_", " ").title(), command=lambda a=app_name: self.launch_app(a))
                app_buttons.append(btn)

        for i, btn in enumerate(app_buttons):
            btn.grid(row=i, column=0, pady=5, sticky="w")

    def launch_app(self, app_name):
        try:
            app_module = importlib.import_module(f"apps.{app_name}.ui")
            app_module.run()
        except Exception as e:
            print(f"Failed to launch {app_name}: {e}")

def launch_ui():
    app = RonynDeskApp()
    app.mainloop()