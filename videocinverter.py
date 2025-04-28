import os
import subprocess
import sys
import threading
import tkinter as tk
from tkinter import filedialog, messagebox

def convert_to_mp4(input_path):
    # Determine output path: same folder, same base name with .mp4
    base, _ = os.path.splitext(input_path)
    output_path = base + '.mp4'

    # Build ffmpeg command
    command = [
        'ffmpeg', '-y',    # overwrite without asking
        '-i', input_path,
        '-c:v', 'libx264',
        '-c:a', 'aac',
        output_path
    ]

    try:
        # Run conversion
        process = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

        if process.returncode == 0:
            messagebox.showinfo("Conversion terminée", f"Le fichier a été converti avec succès en:\n{output_path}")
        else:
            messagebox.showerror("Erreur de conversion", f"Une erreur est survenue lors de la conversion :\n{process.stderr}")
    except FileNotFoundError:
        messagebox.showerror("ffmpeg introuvable", "ffmpeg n'a pas été trouvé. Veuillez l'installer et l'ajouter au PATH.")
    except Exception as e:
        messagebox.showerror("Erreur inattendue", str(e))


def start_conversion(path):
    # Run conversion in a separate thread to keep the GUI responsive
    thread = threading.Thread(target=convert_to_mp4, args=(path,))
    thread.start()


def browse_file():
    # Open file dialog to select video
    filetypes = [
        ("Fichiers vidéo", "*.mp4 *.avi *.mkv *.mov *.flv *.wmv *.webm"),
        ("Tous les fichiers", "*")
    ]
    path = filedialog.askopenfilename(title="Sélectionnez une vidéo à convertir", filetypes=filetypes)
    if path:
        entry_path.delete(0, tk.END)
        entry_path.insert(0, path)


def on_convert():
    path = entry_path.get().strip()
    if not path:
        messagebox.showwarning("Aucun fichier sélectionné", "Veuillez sélectionner un fichier vidéo.")
        return
    if not os.path.isfile(path):
        messagebox.showerror("Fichier introuvable", "Le fichier sélectionné n'existe pas.")
        return
    start_conversion(path)


# GUI setup
root = tk.Tk()
root.title("Convertisseur Vidéo vers MP4")
root.resizable(False, False)

frame = tk.Frame(root, padx=10, pady=10)
frame.pack()

label = tk.Label(frame, text="Chemin du fichier vidéo :")
label.grid(row=0, column=0, sticky="w")

entry_path = tk.Entry(frame, width=50)
entry_path.grid(row=1, column=0, pady=5)

btn_browse = tk.Button(frame, text="Parcourir...", command=browse_file)
btn_browse.grid(row=1, column=1, padx=5)

btn_convert = tk.Button(frame, text="Convertir en MP4", width=20, command=on_convert)
btn_convert.grid(row=2, column=0, columnspan=2, pady=10)

root.mainloop()

# Usage:
# 1. Assurez-vous que ffmpeg est installé et accessible depuis la ligne de commande.
# 2. Lancez ce script : python video_converter_gui.py
# 3. Sélectionnez votre fichier vidéo, puis cliquez sur "Convertir en MP4".
