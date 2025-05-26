def run(*args, **kwargs):
    import tkinter as tk
    from tkinter import simpledialog, messagebox

    parent = kwargs.get("master") or tk.Toplevel()
    parent.title("YouTube Downloader")
    parent.geometry("600x300")
    parent.configure(bg="#111111")

    def download():
        url = simpledialog.askstring("YouTube URL", "Enter the YouTube video URL:", parent=parent)
        if not url:
            return
        try:
            from .downloader import download_video
            download_video(url)
            messagebox.showinfo("Success", "Download completed!", parent=parent)
        except Exception as e:
            messagebox.showerror("Error", str(e), parent=parent)

    label = tk.Label(parent, text="Paste YouTube URL to download", bg="#111111", fg="white", font=("Segoe UI", 12))
    label.pack(pady=20)

    btn = tk.Button(parent, text="Download Video", command=download, bg="#222222", fg="white", font=("Segoe UI", 11, "bold"))
    btn.pack(pady=10)

