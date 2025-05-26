import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import importlib
import os
import sys

APP_DIR = "apps"

class RonynDeskApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("RonynDesk")
        self.configure(bg="#111111")
        self.geometry("1280x720")

        try:
            base_dir = os.path.dirname(os.path.abspath(__file__))
            icon_path_ico = os.path.abspath(os.path.join(base_dir, "..", "assets", "icons", "samurai.ico"))
            icon_path_png = os.path.abspath(os.path.join(base_dir, "..", "assets", "icons", "samurai.png"))
            if os.path.exists(icon_path_ico):
                self.iconbitmap(icon_path_ico)
            if os.path.exists(icon_path_png):
                icon_img = tk.PhotoImage(file=icon_path_png)
                self.iconphoto(False, icon_img)
        except Exception as e:
            print(f"Could not load main window icon: {e}")

        style = ttk.Style(self)
        style.theme_use("default")
        style.configure("TFrame", background="#111111")
        style.configure("TLabel", background="#111111", foreground="white", font=('Segoe UI', 12))
        style.configure("TButton", background="#222222", foreground="white", font=('Segoe UI', 11, 'bold'))

        self.fullscreen = False
        self.icon_images = {}
        self.icon_buttons = []

        self.container = ttk.Frame(self); self.container.pack(fill="both", expand=True, padx=40, pady=20)
        self.load_apps()

    def toggle_fullscreen(self):
        self.fullscreen = not self.fullscreen
        self.attributes("-fullscreen", self.fullscreen)

    def load_apps(self):
        for widget in self.container.winfo_children(): widget.destroy()
        self.icon_buttons.clear()
        row = 0; column = 0

        for app_name in os.listdir(APP_DIR):
            app_path = os.path.join(APP_DIR, app_name)
            icon_png = os.path.join(app_path, "assets", "icon.png")
            icon_ico = os.path.join(app_path, "assets", "icon.ico")

            if os.path.isdir(app_path) and "ui.py" in os.listdir(app_path):
                try:
                    if os.path.exists(icon_png): image = Image.open(icon_png).resize((128, 128))
                    elif os.path.exists(icon_ico): image = Image.open(icon_ico).resize((128, 128))
                    else: raise FileNotFoundError("No valid icon file found.")

                    icon = ImageTk.PhotoImage(image)
                    self.icon_images[app_name] = icon

                    card = tk.Frame(self.container, bg="#1a1a1a", highlightbackground="#444444", highlightthickness=2, bd=0, cursor="hand2")
                    card.grid(row=row, column=column, padx=20, pady=20)

                    def on_enter(e): card.config(bg="#333333"); label.config(bg="#333333"); icon_label.config(bg="#333333")
                    def on_leave(e): card.config(bg="#1a1a1a"); label.config(bg="#1a1a1a"); icon_label.config(bg="#1a1a1a")

                    card.bind("<Button-1>", lambda e, a=app_name: self.open_app_window(a))
                    icon_label = tk.Label(card, image=icon, bg="#1a1a1a"); icon_label.pack(padx=20, pady=(20, 10)); icon_label.bind("<Button-1>", lambda e, a=app_name: self.open_app_window(a))
                    label = tk.Label(card, text=app_name.replace("_", " ").title(), bg="#1a1a1a", fg="white", font=("Segoe UI", 11)); label.pack(pady=(0, 20)); label.bind("<Button-1>", lambda e, a=app_name: self.open_app_window(a))

                    for widget in (card, icon_label, label):
                        widget.bind("<Enter>", on_enter)
                        widget.bind("<Leave>", on_leave)

                    self.icon_buttons.append(card)
                    column += 1
                    if column >= 4: column = 0; row += 1

                except Exception as e:
                    print(f"Error loading icon for {app_name}: {e}")

    def open_app_window(self, app_name):
        self.destroy()
        app_window = tk.Tk()
        app_window.title(f"RonynDesk/{app_name.replace('_', ' ').title()}")
        app_window.configure(bg="#111111")
        app_window.geometry("900x600")

        icon_path_ico = os.path.join(APP_DIR, app_name, "assets", "icon.ico")
        icon_path_png = os.path.join(APP_DIR, app_name, "assets", "icon.png")
        try:
            if os.path.exists(icon_path_ico): app_window.iconbitmap(icon_path_ico)
            if os.path.exists(icon_path_png): icon_img = ImageTk.PhotoImage(Image.open(icon_path_png)); app_window.iconphoto(False, icon_img)
        except Exception as e:
            print(f"Could not load window icon for {app_name}: {e}")

        header = tk.Frame(app_window, bg="#111111"); header.pack(fill="x", padx=20, pady=(10, 0))
        back_btn = tk.Button(header, text="←", command=lambda: self.back_to_main(app_window), bg="#1a1a1a", fg="white", activebackground="#333333", activeforeground="white", font=("Segoe UI", 14), relief="flat", padx=10, pady=5, cursor="hand2"); back_btn.pack(side="left")
        label = tk.Label(header, text=app_name.replace('_', ' ').title(), font=("Segoe UI", 16, "bold"), fg="white", bg="#111111"); label.pack(side="top", pady=(5, 10))

        try:
            app_module = importlib.import_module(f"apps.{app_name}.ui")
            if hasattr(app_module, "run"): app_module.run(master=app_window)
        except Exception as e:
            print(f"Failed to launch {app_name}: {e}")

    def back_to_main(self, current_window):
        current_window.destroy()
        os.execl(sys.executable, sys.executable, *sys.argv)

def launch_ui():
    app = RonynDeskApp()
    app.mainloop()


