import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
from PIL import Image, ImageTk
import subprocess

# Fungsi untuk menangani pilihan dari Combobox
def open_selected_program(event):
    selected_program = program_combobox.get()
    if selected_program == "T Maze Spontaneous Alternation Test":
        subprocess.Popen(["python", "TMazeProgram.py"])
        messagebox.showinfo("Info", "Mengalihkan ke T Maze Spontaneous Alternation Test")
    elif selected_program == "Elevated Plus Maze":
        subprocess.Popen(["python", "PlusMazeProgram.py"])
        messagebox.showinfo("Info", "Mengalihkan ke Elevated Plus Maze")

# Fungsi untuk menyesuaikan gambar background dengan ukuran jendela
def resize_bg(event):
    new_width = event.width
    new_height = event.height
    resized = original_bg.resize((new_width, new_height), Image.Resampling.LANCZOS)
    bg_photo = ImageTk.PhotoImage(resized)
    bg_label.config(image=bg_photo)
    bg_label.image = bg_photo  # Prevent garbage collection

# Membuat jendela utama
root = tk.Tk()
root.title("Animal Model Behavior | Functional and Behavioral Neuroscience Lab")
root.geometry("1200x640")  # Memulai dengan ukuran jendela yang lebih besar untuk tampilan yang lebih baik

# Memuat gambar background
original_bg = Image.open("Image/tikus.jpeg")

# Menambahkan label untuk gambar background
bg_photo = ImageTk.PhotoImage(original_bg)
bg_label = tk.Label(root, image=bg_photo)
bg_label.place(x=0, y=0, relwidth=1, relheight=1)

# Mengikat event resize untuk menyesuaikan gambar background
root.bind("<Configure>", resize_bg)

# Menambahkan frame untuk menampung widget agar teks tetap terbaca
frame = tk.Frame(root, bd=0, highlightthickness=0)
frame.place(relx=0.5, rely=0.5, anchor='center')

# Menambahkan label judul dengan gaya modern
title_label = tk.Label(frame, text="Animal Model Behavior\nFunctional and Behavioral Neuroscience Lab",
                       font=("Helvetica", 20, "bold"), bg='white', fg='#2c3e50', justify='center')
title_label.pack(pady=20)

# Menambahkan Combobox untuk memilih program dengan gaya modern
style = ttk.Style()
style.theme_use('clam')
style.configure("TCombobox",
                fieldbackground="white",
                background="white",
                foreground="#2c3e50",
                borderwidth=1,
                relief="flat",
                padding=10)

program_combobox = ttk.Combobox(frame,
                                values=["T Maze Spontaneous Alternation Test", "Elevated Plus Maze"],
                                font=("Helvetica", 12),
                                style="TCombobox",
                                state="readonly")
program_combobox.set("Menu")
program_combobox.pack(pady=10)
program_combobox.bind("<<ComboboxSelected>>", open_selected_program)

# Menjalankan aplikasi
root.mainloop()
