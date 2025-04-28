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
#               Joue une vidéo spécifique selon l'identifiant.
#               Bouton Accueil pour revenir à l'écran d'accueil à tout moment.
#               Installez : brew install vlc && pip install python-vlc
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
VIDEO_PATH_DEFAULT = "video.mp4"
USER_VIDEOS = {
    "alice": "video_alice.mp4",
    "bob": "video_bob.mp4",
    "charlie": "video_charlie.mp4"
}

class CodeAccessApp:
    def __init__(self, master):
        self.master = master
        self.attempts = {}
        self.video_to_play = VIDEO_PATH_DEFAULT

        master.title("POLICE SERVER TERMINAL")
        master.attributes('-fullscreen', True)
        master.configure(bg="black")
        master.resizable(False, False)
        master.bind('<Escape>', lambda e: master.destroy())

        # Bouton Accueil toujours visible
        self.home_button = tk.Button(master, text="ACCUEIL", command=self._home,
                                     fg="#00FF00", bg="black", font=("Courier",14), bd=0,
                                     activebackground="black", activeforeground="#00FF00")
        self.home_button.pack(anchor='nw', padx=20, pady=20)

        # Message principal
        self.conn_label = tk.Label(master, text="", fg="#00FF00", bg="black",
                                   font=("Courier",36,"bold"))

        # Titre
        self.title_label = tk.Label(master,
                                    text=">> POLICE SERVER TERMINAL <<",
                                    fg="#00FF00", bg="black",
                                    font=("Courier",28,"bold"))
        self.title_label.pack(pady=(40,10))

        # Zone de saisie
        self.input_frame = tk.Frame(master, bg="black")
        self.input_frame.pack(pady=20)
        tk.Label(self.input_frame, text="USER ID:", fg="#00FF00", bg="black",
                 font=("Courier",20)).grid(row=0,column=0,padx=(0,15),pady=5,sticky='e')
        self.user_entry = tk.Entry(self.input_frame, fg="#00FF00", bg="black",
                                   insertbackground="#00FF00", font=("Courier",20), width=25, bd=0)
        self.user_entry.grid(row=0,column=1,pady=5)
        tk.Label(self.input_frame, text="PASSWORD:", fg="#00FF00", bg="black",
                 font=("Courier",20)).grid(row=1,column=0,padx=(0,15),pady=5,sticky='e')
        self.pwd_entry = tk.Entry(self.input_frame, show="*", fg="#00FF00", bg="black",
                                  insertbackground="#00FF00", font=("Courier",20), width=25, bd=0)
        self.pwd_entry.grid(row=1,column=1,pady=5)
        self.user_entry.focus_set()

        # Bouton EXECUTE
        self.submit_button = tk.Button(master, text="EXECUTE", command=self.start_fake_loading,
                                       fg="#00FF00", bg="black", font=("Courier",20), bd=0,
                                       activebackground="black", activeforeground="#00FF00")
        self.submit_button.pack()

        # Faux terminal
        self.fake_area = tk.Text(master, bg="black", fg="#00FF00",
                                 font=("Courier",14), bd=0, highlightthickness=0)

        # Label statut (tentatives ou countdown)
        self.status_label = tk.Label(master, text="", fg="#00FF00", bg="black",
                                     font=("Courier",18))
        self.status_label.pack(pady=20)

        # Bouton RESET
        self.reset_button = tk.Button(master, text="RESET", command=self.reset_ui,
                                      fg="#00FF00", bg="black", font=("Courier",20), bd=0,
                                      activebackground="black", activeforeground="#00FF00")

    def _home(self):
        self._hide_all_widgets(exclude_home=True)
        self.title_label.pack(pady=(40,10))
        self.input_frame.pack(pady=20)
        self.submit_button.pack()
        self.status_label.config(text="")
        self.status_label.pack(pady=20)
        self.user_entry.config(state=tk.NORMAL)
        self.pwd_entry.config(state=tk.NORMAL)
        self.user_entry.delete(0,tk.END)
        self.pwd_entry.delete(0,tk.END)
        self.user_entry.focus_set()

    def start_fake_loading(self):
        self._hide_all_widgets(exclude_home=True)
        self.fake_area.pack(fill=tk.BOTH, expand=True)
        self.fake_area.delete(1.0,tk.END)
        self.fake_area.insert(tk.END,
                              "Connecting to 192.168.0.1...\n"
                              "Initiating secure tunnel...\n"
                              "Authenticating credentials...\n\n")
        self.load_cycles = 60
        self.load_delay = 60
        self.fake_load_cycle()

    def fake_load_cycle(self):
        if self.load_cycles>0:
            if random.random()<0.05:
                self.fake_area.config(bg="#330000",fg="#FF3333")
            else:
                self.fake_area.config(bg="black",fg="#00FF00")
            line=''.join(random.choice('0123456789ABCDEF') for _ in range(80))
            self.fake_area.insert(tk.END,line+'\n')
            self.fake_area.see(tk.END)
            self.load_cycles-=1
            self.master.after(self.load_delay,self.fake_load_cycle)
        else:
            self.fake_area.pack_forget()
            self.fake_area.config(bg="black",fg="#00FF00")
            self.evaluate_credentials()

    def evaluate_credentials(self):
        user=self.user_entry.get()
        pwd=self.pwd_entry.get()
        # Vérifier existence de l'ID
        if user not in AUTHORIZED_USERS:
            self.status_label.config(text="ID inexistant",fg="red")
            self.status_label.pack(pady=20)
            self.master.after(2000,lambda:self.reset_ui(show_entries=True))
            return
        tries=self.attempts.get(user,0)
        remaining=MAX_ATTEMPTS-tries
        # Admin unlock
        if pwd==ADMIN_PASSWORD and tries>=MAX_ATTEMPTS:
            self.attempts[user]=0
            text="ACCOUNT UNLOCKED"
            color="#00FF00"
            self.status_label.config(text="Account unlocked",fg="#00FF00")
            self.status_label.pack(pady=20)
            self.conn_label.config(text=text,fg=color)
            self.conn_label.pack(expand=True)
            self.master.after(2000,lambda:self.reset_ui(show_entries=True))
            return
        if tries>=MAX_ATTEMPTS:
            text="ACCOUNT LOCKED"
            color="red"
            self.status_label.config(text="Account locked",fg="red")
            self.status_label.pack(pady=20)
            self.conn_label.config(text=text,fg=color)
            self.conn_label.pack(expand=True)
            self.master.after(2000,lambda:self.reset_ui(show_entries=True))
            return
        # Authentification normale
        if AUTHORIZED_USERS[user]==pwd:
            text="CONNECTION APPROVED"
            color="#00FF00"
            self.attempts[user]=0
            self.video_to_play=USER_VIDEOS.get(user,VIDEO_PATH_DEFAULT)
            self.conn_label.config(text=text,fg=color)
            self.conn_label.pack(expand=True)
            self.master.after(2000,self._start_countdown)
        else:
            # Mauvais mot de passe
            self.attempts[user]=tries+1
            remaining-=1
            if remaining>0:
                text="CONNECTION DENIED"
                color="red"
                self.status_label.config(text=f"Tentatives restantes : {remaining}",fg="red")
            else:
                text="ACCOUNT LOCKED"
                color="red"
                self.status_label.config(text="Account locked",fg="red")
            self.status_label.pack(pady=20)
            self.conn_label.config(text=text,fg=color)
            self.conn_label.pack(expand=True)
            self.master.after(2000,lambda:self.reset_ui(show_entries=True))

    def _start_countdown(self):
        self.conn_label.pack_forget()
        self.status_label.config(text="",fg="#00FF00")
        self.status_label.pack(pady=20)
        self.countdown(3)

    def countdown(self,remaining):
        if remaining<=0:
            self.play_video()
        else:
            self.status_label.config(text=f"Launching in {remaining}...",fg="#00FF00")
            self.master.after(1000,lambda:self.countdown(remaining-1))

    def play_video(self):
        args=["--fullscreen","--play-and-exit","--start-time=0",self.video_to_play]
        if sys.platform.startswith('darwin'):
            vlc_exec="/Applications/VLC.app/Contents/MacOS/VLC"
            if os.path.exists(vlc_exec):
                subprocess.call([vlc_exec]+args)
            else:
                subprocess.call(['open','-a','VLC','--args']+args)
        elif os.name=='nt':
            vlc_path=r"C:\Program Files\VideoLAN\VLC\vlc.exe"
            if os.path.exists(vlc_path):
                subprocess.call([vlc_path]+args)
            else:
                os.startfile(self.video_to_play)
        elif os.name=='posix':
            subprocess.call(['vlc']+args)
        else:
            messagebox.showinfo("Info",f"Lancez manuellement : {self.video_to_play}")

    def reset_ui(self,show_entries=False):
        self._hide_all_widgets(exclude_home=True)
        self.title_label.pack(pady=(40,10))
        self.input_frame.pack(pady=20)
        self.submit_button.pack()
        if show_entries:
            self.user_entry.delete(0,tk.END)
            self.pwd_entry.delete(0,tk.END)
        self.user_entry.config(state=tk.NORMAL)
        self.pwd_entry.config(state=tk.NORMAL)
        self.status_label.config(text="",fg="#00FF00")
        self.status_label.pack(pady=20)

    def _hide_all_widgets(self,exclude_home=False):
        for widget in [self.title_label,self.input_frame,self.submit_button,
                       self.fake_area,self.conn_label,self.status_label,self.reset_button]:
            try:
                widget.pack_forget()
            except:
                pass
        if not exclude_home:
            self.home_button.pack_forget()

if __name__=="__main__":
    root=tk.Tk()
    app=CodeAccessApp(root)
    root.mainloop()