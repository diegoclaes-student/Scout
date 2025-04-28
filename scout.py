# -*- coding: utf-8 -*-
import tkinter as tk
from tkinter import messagebox
import os
import sys
import subprocess
import random

# --------------------------------------------------
# Script : jeu_scout_modifié.py
# Description : Interface graphique simulant un "serveur de la police" en style terminal plein écran.
#               Authentification par identifiant et mot de passe.
#               Limite de tentatives par utilisateur, possibilité de déverrouillage avec mot de passe admin.
#               Affiche le nombre de tentatives restantes après chaque essai.
#               Affiche faux code, connexion, puis ouvre la vidéo en plein écran depuis le début.
#               Installer : brew install vlc && pip install python-vlc
# --------------------------------------------------

# CONFIGURATION :
AUTHORIZED_USERS = {
    "admin": "",
    "alice": "alpha123",
    "bob": "bravo456",
    "charlie": "charlie789"
}
MAX_ATTEMPTS = 3
ADMIN_PASSWORD = "admin"
VIDEO_PATH = "video.mp4"

class CodeAccessApp:
    def __init__(self, master):
        self.master = master
        # Stocke le nombre de tentatives par utilisateur
        self.attempts = {}

        master.title("POLICE SERVER TERMINAL")
        master.attributes('-fullscreen', True)
        master.configure(bg="black")
        master.resizable(False, False)
        master.bind('<Escape>', lambda e: master.destroy())

        # Connexion result label
        self.conn_label = tk.Label(master, text="", fg="#00FF00", bg="black",
                                   font=("Courier", 36, "bold"))

        # Titre et saisie
        self.title_label = tk.Label(master,
                                    text=">> POLICE SERVER TERMINAL <<",
                                    fg="#00FF00", bg="black",
                                    font=("Courier", 28, "bold"))
        self.title_label.pack(pady=(40, 10))

        # Frame pour identifiant et mot de passe
        self.input_frame = tk.Frame(master, bg="black")
        self.input_frame.pack(pady=20)
        tk.Label(self.input_frame,
                 text="USER ID:", fg="#00FF00", bg="black",
                 font=("Courier", 20)).grid(row=0, column=0, padx=(0,15), pady=5, sticky='e')
        self.user_entry = tk.Entry(self.input_frame,
                                   fg="#00FF00", bg="black",
                                   insertbackground="#00FF00",
                                   font=("Courier",20), width=25, bd=0)
        self.user_entry.grid(row=0, column=1, pady=5)

        tk.Label(self.input_frame,
                 text="PASSWORD:", fg="#00FF00", bg="black",
                 font=("Courier", 20)).grid(row=1, column=0, padx=(0,15), pady=5, sticky='e')
        self.pwd_entry = tk.Entry(self.input_frame,
                                  show="*", fg="#00FF00", bg="black",
                                  insertbackground="#00FF00",
                                  font=("Courier",20), width=25, bd=0)
        self.pwd_entry.grid(row=1, column=1, pady=5)
        self.user_entry.focus_set()

        self.submit_button = tk.Button(master,
                                       text="EXECUTE", command=self.start_fake_loading,
                                       fg="#00FF00", bg="black",
                                       font=("Courier",20), bd=0,
                                       activebackground="black", activeforeground="#00FF00")
        self.submit_button.pack()

        # Zone de faux code
        self.fake_area = tk.Text(master,
                                 bg="black", fg="#00FF00",
                                 font=("Courier",14), bd=0,
                                 highlightthickness=0)

        # Label de statut (pour tentatives restantes)
        self.status_label = tk.Label(master, text="",
                                     fg="#00FF00", bg="black",
                                     font=("Courier",18))
        self.status_label.pack(pady=20)

        # Bouton RESET
        self.reset_button = tk.Button(master, text="RESET",
                                      command=self.reset_ui,
                                      fg="#00FF00", bg="black",
                                      font=("Courier",20), bd=0,
                                      activebackground="black", activeforeground="#00FF00")

    def start_fake_loading(self):
        self._hide_initial_widgets()
        self.fake_area.pack(fill=tk.BOTH, expand=True)
        self.fake_area.delete(1.0, tk.END)
        self.fake_area.insert(tk.END,
                              "Connecting to 192.168.0.1...\n"
                              "Initiating secure tunnel...\n"
                              "Authenticating credentials...\n\n"
                              )
        self.load_cycles = 60
        self.load_delay = 60
        self.fake_load_cycle()

    def fake_load_cycle(self):
        if self.load_cycles > 0:
            if random.random() < 0.05:
                self.fake_area.config(bg="#330000", fg="#FF3333")
            else:
                self.fake_area.config(bg="black", fg="#00FF00")
            line = ''.join(random.choice('0123456789ABCDEF') for _ in range(80))
            self.fake_area.insert(tk.END, line + '\n')
            self.fake_area.see(tk.END)
            self.load_cycles -= 1
            self.master.after(self.load_delay, self.fake_load_cycle)
        else:
            self.fake_area.pack_forget()
            self.fake_area.config(bg="black", fg="#00FF00")
            self.evaluate_credentials()

    def evaluate_credentials(self):
        user = self.user_entry.get()
        pwd = self.pwd_entry.get()
        tries = self.attempts.get(user, 0)
        remaining = MAX_ATTEMPTS - tries

        # Vérification admin pour déverrouillage
        if pwd == ADMIN_PASSWORD and tries >= MAX_ATTEMPTS:
            self.attempts[user] = 0
            text = "ACCOUNT UNLOCKED"
            color = "#00FF00"
            locked = False
            success = False
        else:
            if tries >= MAX_ATTEMPTS:
                text = "ACCOUNT LOCKED"
                color = "red"
                locked = True
                success = False
            else:
                if pwd == ADMIN_PASSWORD:
                    text = "NO LOCK TO UNLOCK"
                    color = "#00FF00"
                    locked = False
                    success = False
                elif AUTHORIZED_USERS.get(user) == pwd:
                    text = "CONNECTION APPROVED"
                    color = "#00FF00"
                    success = True
                    locked = False
                    self.attempts[user] = 0
                else:
                    tries += 1
                    self.attempts[user] = tries
                    remaining = MAX_ATTEMPTS - tries
                    text = ("ACCOUNT LOCKED" if tries >= MAX_ATTEMPTS else "CONNECTION DENIED")
                    color = "red"
                    locked = tries >= MAX_ATTEMPTS
                    success = False
                    # Affichage tentatives restantes si non verrouillé
                    if not locked:
                        self.status_label.config(text=f"Tentatives restantes : {remaining}", fg="red")
                        self.status_label.pack()

        # Affichage du résultat principal
        suffix = f" ({remaining} left)" if "DENIED" in text else ""
        self.conn_label.config(text=text + suffix, fg=color)
        self.conn_label.pack(expand=True)
        self.master.after(2000, lambda: self._after_connection(success, locked))

    def _after_connection(self, success, locked):
        self.conn_label.pack_forget()
        if success:
            self.on_access_granted()
        else:
            if locked:
                messagebox.showwarning("Verrouillage", "Trop de tentatives. Le compte est verrouillé.")
            # revient toujours à saisie pour les autres
            self.reset_ui(show_entries=True)

    def on_access_granted(self):
        self.user_entry.config(state=tk.DISABLED)
        self.pwd_entry.config(state=tk.DISABLED)
        # Cache le message d'erreur précédent
        self.status_label.pack_forget()
        self.status_label.config(text="", fg="#00FF00")
        self.status_label.pack()
        self.countdown(3, callback=self.play_video)
        self.reset_button.pack(pady=10)
        self.start_blinking_reset()

    def reset_ui(self, show_entries=False):
        # Ne pas cacher le statut si on revient après une erreur
        self.fake_area.pack_forget()
        self.conn_label.pack_forget()
        if not show_entries:
            self.status_label.pack_forget()
            self.status_label.config(text="", fg="#00FF00")
        self.reset_button.pack_forget()
        self.title_label.pack(pady=(40,10))
        self.input_frame.pack(pady=20)
        self.submit_button.pack()
        if show_entries:
            self.user_entry.delete(0, tk.END)
            self.pwd_entry.delete(0, tk.END)
        self.user_entry.config(state=tk.NORMAL)
        self.pwd_entry.config(state=tk.NORMAL)
        self.user_entry.focus_set()

    def _hide_initial_widgets(self):
        for w in [self.title_label, self.input_frame, self.submit_button, self.status_label, self.reset_button]:
            w.pack_forget()


def main():
    root = tk.Tk()
    app = CodeAccessApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
#test