def run():
    import tkinter as tk
    from tkinter import simpledialog, messagebox

    def download():
        url = simpledialog.askstring("YouTube URL", "Enter the YouTube video URL:")
        if not url:
            return
        try:
            from .downloader import download_video
            download_video(url)
            messagebox.showinfo("Success", "Download completed!")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    win = tk.Toplevel()
    win.title("YouTube Downloader")
    win.geometry("400x200")
    win.configure(bg="#111111")

    btn = tk.Button(win, text="Download Video", command=download, bg="#222222", fg="white")
    btn.pack(pady=60)
