import tkinter as tk
from tkinter import filedialog, messagebox
import pyttsx3
from pypdf import PdfReader

# Initialize TTS engine
engine = pyttsx3.init()

def browse_pdf():
    file_path = filedialog.askopenfilename(
        filetypes=[("PDF Files", "*.pdf")],
        title="Select PDF File"
    )
    if file_path:
        pdf_path_var.set(file_path)

def read_pdf():
    file_path = pdf_path_var.get()
    try:
        page_num = int(page_entry.get())
        reader = PdfReader(file_path)
        if page_num < 0 or page_num >= len(reader.pages):
            messagebox.showerror("Error", f"Page number out of range (0 - {len(reader.pages) - 1})")
            return
        page = reader.pages[page_num]
        text = page.extract_text()
        if not text:
            messagebox.showinfo("No Text", "No text found on this page.")
            return

        # Set speech speed from slider
        speed = speed_scale.get()
        engine.setProperty('rate', speed)

        engine.say(text)
        engine.runAndWait()
    except Exception as e:
        messagebox.showerror("Error", str(e))

# GUI setup
root = tk.Tk()
root.title("PDF Audiobook Reader")
root.geometry("400x320")
root.resizable(False, False)

pdf_path_var = tk.StringVar()

tk.Label(root, text="Select a PDF file:").pack(pady=5)
tk.Entry(root, textvariable=pdf_path_var, width=40).pack(pady=5)
tk.Button(root, text="Browse", command=browse_pdf).pack(pady=5)

tk.Label(root, text="Enter Page Number:").pack(pady=5)
page_entry = tk.Entry(root)
page_entry.pack(pady=5)

# 🔊 Add Speech Speed Control
tk.Label(root, text="Speech Speed:").pack(pady=5)
speed_scale = tk.Scale(root, from_=100, to=300, orient=tk.HORIZONTAL)
speed_scale.set(175)  # Default speed
speed_scale.pack(pady=5)

tk.Button(root, text="Read Aloud", command=read_pdf, bg="green", fg="white").pack(pady=15)

tk.Label(root, text="Created with ❤️ using Python", font=("Arial", 8)).pack(side=tk.BOTTOM, pady=5)

root.mainloop()
