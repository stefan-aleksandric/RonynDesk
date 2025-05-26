import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from threading import Thread
from yt_dlp import YoutubeDL
import os
import webbrowser
import queue
import json
import platform
import subprocess


def run(*args, **kwargs):
    master = kwargs.get("master") or tk.Toplevel()
    master.title("VisionRipper")
    master.geometry("750x550")
    master.configure(bg="#111111")

    save_path = os.path.join(os.path.expanduser("~"), "Downloads")
    history_file = os.path.join(os.path.dirname(__file__), "history.json")
    event_queue = queue.Queue()

    def load_history():
        if os.path.exists(history_file):
            try:
                with open(history_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                return []
        return []

    def save_history():
        try:
            with open(history_file, "w", encoding="utf-8") as f:
                json.dump(history, f, indent=2)
        except Exception as e:
            print(f"Failed to save history: {e}")

    history = load_history()

    def start_download():
        url = url_entry.get().strip()
        if not url:
            messagebox.showwarning("Missing URL", "Please enter a video URL.", parent=master)
            return

        progress_var.set(0)
        status_label.config(text="Starting download...")

        def download():
            try:
                ydl_opts = {
                    'outtmpl': os.path.join(save_path, '%(title)s.%(ext)s'),
                    'format': 'best',
                    'progress_hooks': [progress_hook],
                    'noplaylist': True,
                    'quiet': False,
                    'no_warnings': True
                }
                with YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(url, download=True)
                    filename = ydl.prepare_filename(info)
                    history.append(filename)
                    save_history()
                    event_queue.put(('complete', filename))
            except Exception as e:
                event_queue.put(('error', str(e)))

        Thread(target=download, daemon=True).start()

    def progress_hook(d):
        if d['status'] == 'downloading':
            downloaded = d.get('downloaded_bytes', 0)
            total = d.get('total_bytes', 1)
            percent = int((downloaded / total) * 100)
            event_queue.put(('progress', percent))

    def process_queue():
        try:
            while True:
                event = event_queue.get_nowait()
                if event[0] == 'progress':
                    progress_var.set(event[1])
                elif event[0] == 'complete':
                    status_label.config(text="Download complete.")
                    update_history()
                elif event[0] == 'error':
                    status_label.config(text="Download failed.")
                    messagebox.showerror("Download Error", event[1], parent=master)
        except queue.Empty:
            pass
        master.after(100, process_queue)

    def choose_folder():
        nonlocal save_path
        selected = filedialog.askdirectory(initialdir=save_path)
        if selected:
            save_path = selected
            folder_label.config(text=f"Save to: {save_path}")

    def open_latest():
        if history:
            filepath = history[-1]
            if os.path.exists(filepath):
                webbrowser.open(filepath)

    def open_folder():
        if os.path.exists(save_path):
            if platform.system() == "Windows":
                os.startfile(save_path)
            elif platform.system() == "Darwin":
                subprocess.call(["open", save_path])
            else:
                subprocess.call(["xdg-open", save_path])

    def open_selected(event):
        selection = history_list.curselection()
        if selection:
            index = selection[0]
            label = history_list.get(index)
            filename = label.split(" | ")[0]
            full_path = os.path.join(save_path, filename)
            if os.path.exists(full_path):
                webbrowser.open(full_path)

    def delete_selected(event):
        selection = history_list.curselection()
        if selection:
            index = selection[0]
            filename = history_list.get(index)
            full_path = None
            for item in history:
                if os.path.basename(item) == filename:
                    full_path = item
                    break
            confirm = messagebox.askyesno("Delete File", f"Delete '{filename}' from disk and history?", parent=master)
            if confirm and full_path:
                try:
                    if os.path.exists(full_path):
                        os.remove(full_path)
                    for i, item in enumerate(history):
                        if os.path.basename(item) == filename:
                            del history[i]
                            break
                    save_history()
                    update_history()
                except Exception as e:
                    messagebox.showerror("Error", f"Could not delete file: {e}", parent=master)

    def rename_selected():
        selection = history_list.curselection()
        if selection:
            index = selection[0]
            label = history_list.get(index)
            old_name = label.split(" | ")[0]
            old_path = None
            for item in history:
                if os.path.basename(item) == old_name:
                    old_path = item
                    break
            if old_path and os.path.exists(old_path):
                new_name = filedialog.asksaveasfilename(defaultextension=os.path.splitext(old_path)[1], initialfile=old_name, initialdir=save_path)
                if new_name and new_name != old_path:
                    try:
                        os.rename(old_path, new_name)
                        history[index] = new_name
                        save_history()
                        update_history()
                    except Exception as e:
                        messagebox.showerror("Rename Error", str(e), parent=master)

    def update_history():
        history_list.delete(0, tk.END)
        to_keep = []
        query = search_var.get().strip().lower() if 'search_var' in globals() or 'search_var' in locals() else ""
        for item in reversed(history):
            name = os.path.basename(item)
            if query and query not in name.lower():
                continue
            if os.path.exists(item):
                size = os.path.getsize(item) // 1024
                ext = os.path.splitext(item)[1][1:].upper()
                date = os.path.getmtime(item)
                from datetime import datetime
                date_str = datetime.fromtimestamp(date).strftime('%Y-%m-%d')
                label = f"{name} | {size} KB | {ext} | {date_str}"
                history_list.insert(tk.END, label)
                to_keep.append(item)
        if to_keep != history:
            history.clear()
            history.extend(reversed(to_keep))
            save_history()

    title_label = tk.Label(master, text="Vision Ripper", bg="#111111", fg="white", font=("Segoe UI", 14, "bold"))
    title_label.pack(pady=(10, 5))

    container = tk.Frame(master, bg="#111111")
    container.place(relx=0.5, rely=0.1, anchor="n")

    url_label = tk.Label(container, text="Video URL:", bg="#111111", fg="white", font=("Segoe UI", 11))
    url_label.pack(anchor="w")

    url_entry = tk.Entry(container, width=65, font=("Segoe UI", 11), bg="#1a1a1a", fg="white", insertbackground="white")
    url_entry.insert(0, "Paste video URL here...")
    url_entry.bind("<FocusIn>", lambda e: url_entry.delete(0, tk.END) if url_entry.get() == "Paste video URL here..." else None)
    url_entry.pack(pady=5, anchor="w")

    folder_label = tk.Label(container, text=f"Save to: {save_path}", bg="#111111", fg="grey", font=("Segoe UI", 9))
    folder_label.pack(anchor="w")

    browse_btn = tk.Button(container, text="Choose Folder", command=choose_folder, bg="#222222", fg="white", font=("Segoe UI", 10))
    browse_btn.pack(pady=(5, 10), anchor="w")

    download_btn = tk.Button(container, text="⟳ Download", command=start_download, bg="#007ACC", fg="white", font=("Segoe UI", 12, "bold"))
    download_btn.pack(anchor="w")

    open_btn = tk.Button(container, text="▶ Open Last Video", command=open_latest, bg="#444444", fg="white", font=("Segoe UI", 10))
    open_btn.pack(pady=(5, 0), anchor="w")

    folder_btn = tk.Button(container, text="📁 Open Folder", command=open_folder, bg="#444444", fg="white", font=("Segoe UI", 10))
    folder_btn.pack(pady=(5, 10), anchor="w")

    progress_var = tk.IntVar()
    progress = ttk.Progressbar(container, variable=progress_var, maximum=100)
    progress.pack(fill="x", pady=10, anchor="w")

    status_label = tk.Label(container, text="", bg="#111111", fg="grey", font=("Segoe UI", 9))
    status_label.pack(anchor="w")

    search_var = tk.StringVar()
    search_entry = tk.Entry(container, textvariable=search_var, width=40, font=("Segoe UI", 10), bg="#1a1a1a", fg="white", insertbackground="white")
    search_entry.pack(pady=(10, 5), anchor="w")
    search_entry.insert(0, "Search downloads...")
    search_entry.bind("<KeyRelease>", lambda e: update_history())

    clear_btn = tk.Button(container, text="🧹 Clear Filter", command=lambda: (search_var.set(""), update_history()), bg="#333333", fg="white", font=("Segoe UI", 9))
    clear_btn.pack(anchor="e")

    history_label = tk.Label(container, text="Recent Downloads (double-click to open, right-click to delete):", bg="#111111", fg="white", font=("Segoe UI", 10, "bold"))", bg="#111111", fg="white", font=("Segoe UI", 10, "bold"))
    history_label.pack(anchor="w", pady=(10, 0))

    history_scroll = tk.Scrollbar(container, orient="vertical")
    history_list = tk.Listbox(container, bg="#1a1a1a", fg="white", font=("Segoe UI", 9), height=5, highlightthickness=0, relief="flat", yscrollcommand=history_scroll.set)
    history_scroll.config(command=history_list.yview)








