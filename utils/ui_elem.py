import tkinter as tk
from tkinter import filedialog, ttk


# Classe pour créer un cadre réductible (collapsible)
class CollapsibleFrame(ttk.Frame):
    def __init__(self, master, text="", *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        # Variable pour savoir si la section est ouverte ou fermée
        self.show = tk.BooleanVar(value=True)

        # Création du header avec le bouton pour ouvrir/fermer la section
        header = ttk.Frame(self)
        header.pack(fill="x")

        # Icône pour afficher/masquer la section
        self.icon_label = ttk.Label(header, text="▼", width=2)
        self.icon_label.pack(side="left")
        self.icon_label.bind("<Button-1>", lambda e: self.toggle(force_toggle=True))  # Action pour basculer la visibilité

        # Bouton pour ouvrir/fermer la section
        self.toggle_button = ttk.Checkbutton(
            header, text=text, style="Toolbutton", variable=self.show, command=self.toggle
        )
        self.toggle_button.pack(side="left", fill="x", expand=True, pady=2)

        # Cadre pour le contenu de la section
        self.sub_frame = ttk.Frame(self)
        self.sub_frame.pack(fill="both", expand=True)

    def toggle(self, force_toggle=False):
        """ Bascule l'affichage de la section repliable. """
        if force_toggle:
            self.show.set(not self.show.get())  # Force le basculement si nécessaire

        # Affiche ou cache la section selon l'état de `show`
        if self.show.get():
            self.sub_frame.pack(fill="both", expand=True)
            self.icon_label.configure(text="▼")  # Change l'icône pour indiquer l'ouverture
        else:
            self.sub_frame.forget()  # Cache la section
            self.icon_label.configure(text="▶")  # Change l'icône pour indiquer la fermeture

    def get_frame(self):
        """ Retourne le sous-cadre (sub_frame) contenant le contenu. """
        return self.sub_frame
