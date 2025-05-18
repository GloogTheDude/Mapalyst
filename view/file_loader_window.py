import tkinter as tk
from tkinter import filedialog, ttk
import os
import json
import pandas as pd
from model.extractor import Extractor
from utils.ui_elem import CollapsibleFrame

# Dans la classe FileLoaderWindow

class FileLoaderWindow(tk.Frame):
    def __init__(self, master, controller):
        super().__init__(master)
        self.controller = controller  # Le contrôleur qui gère l'application
        self.extractor = Extractor()  # Objet pour extraire les données des fichiers Excel

        # Cadre pour les boutons (Charger, Ajouter, Sauvegarder, etc.)
        button_frame = tk.Frame(self)
        button_frame.pack(pady=5)

        # Boutons pour charger des fichiers, ajouter un fichier, sauvegarder et charger une configuration précédente
        tk.Button(button_frame, text="Charger des fichiers Excel", command=self.load_file).pack(side="left", padx=5)
        tk.Button(button_frame, text="Ajouter un fichier Excel", command=self.add_file).pack(side="left", padx=5)
        tk.Button(button_frame, text="Sauvegarder et continuer", command=self.save_and_continue).pack(side="left", padx=5)
        tk.Button(button_frame, text="Charger précédent travail", command=self.load_previous_config).pack(side="left", padx=5)

        # Cadre pour afficher le contenu de façon défilable
        container_frame = tk.Frame(self)
        container_frame.pack(fill="both", expand=True)

        # Création du canevas pour permettre le défilement
        self.canvas = tk.Canvas(container_frame)
        scrollbar = tk.Scrollbar(container_frame, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas)

        # Met à jour la zone défilable lorsque la taille change
        self.scrollable_frame.bind(
            "<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        # Crée la fenêtre défilable dans le canevas
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Gestion des événements pour la molette de la souris et les touches fléchées
        self.scrollable_frame.bind_all("<MouseWheel>", self._on_mousewheel)
        self.scrollable_frame.bind_all("<Button-4>", self._on_mousewheel)
        self.scrollable_frame.bind_all("<Button-5>", self._on_mousewheel)
        self.canvas.bind_all("<Up>", self._on_arrow)
        self.canvas.bind_all("<Down>", self._on_arrow)

    def _on_mousewheel(self, event):
        """ Permet de faire défiler avec la molette de la souris. """
        if event.num == 5 or event.delta < 0:
            self.canvas.yview_scroll(1, "units")
        elif event.num == 4 or event.delta > 0:
            self.canvas.yview_scroll(-1, "units")

    def _on_arrow(self, event):
        """ Permet de faire défiler avec les touches fléchées haut et bas. """
        if event.keysym == "Down":
            self.canvas.yview_scroll(1, "units")
        elif event.keysym == "Up":
            self.canvas.yview_scroll(-1, "units")

    def set_controller(self, controller):
        """ Définit le contrôleur principal. """
        self.controller = controller
        # Initialise les métadonnées des colonnes si elles n'existent pas déjà
        if not hasattr(self.controller.data_manager, 'sheet_column_metadata'):
            self.controller.data_manager.sheet_column_metadata = {}

    def load_file(self):
        """ Charge plusieurs fichiers Excel via un sélecteur de fichiers. """
        if not self.controller or not self.controller.data_manager:
            print("Erreur : contrôleur non défini.")
            return

        # Demande à l'utilisateur de sélectionner des fichiers Excel
        paths = filedialog.askopenfilenames(filetypes=[("Excel Files", "*.xlsx *.xls")])
        for path in paths:
            self.import_file(path)  # Charge chaque fichier sélectionné

    def add_file(self):
        """ Ajoute un fichier Excel à la liste. """
        path = filedialog.askopenfilename(filetypes=[("Excel Files", "*.xlsx *.xls")])
        if path:
            self.import_file(path)

    def import_file(self, path, config_for_file=None):
        """ Importe un fichier et l'affiche dans la fenêtre. """
        if path not in self.controller.data_manager.file_frames:
            loaded_file = self.extractor.create_file(path)  # Crée un objet représentant le fichier Excel
            self.controller.data_manager.files.append(loaded_file)  # Ajoute le fichier à la liste des fichiers
            self.display_file(loaded_file, config_for_file)  # Affiche le fichier dans l'interface graphique

    def display_file(self, loaded_file, config_for_file=None):
        """ Affiche le fichier et ses feuilles dans la fenêtre. """
        # Crée un cadre réductible pour chaque fichier
        file_frame = CollapsibleFrame(self.scrollable_frame, text=os.path.basename(loaded_file.path))
        file_frame.pack(fill="x", padx=10, pady=5, expand=True)
        self.controller.data_manager.file_frames[loaded_file.path] = file_frame  # Garde une trace de ce fichier

        # Affiche chaque feuille dans le fichier
        for sheet in loaded_file.sheets:
            sheet_config = config_for_file.get(sheet.name, {}) if config_for_file else {}
            sheet_frame = CollapsibleFrame(file_frame.get_frame(), text=sheet.name)  # Crée un cadre réductible pour chaque feuille
            sheet_frame.pack(fill="x", padx=10, pady=5)

            # Affiche les colonnes de chaque feuille avec une case à cocher
            for col in sheet.dataframe.columns:
                row_frame = tk.Frame(sheet_frame.get_frame())
                row_frame.pack(fill="x", anchor="w")

                # Récupère les informations sur la colonne, notamment si elle est sélectionnée
                col_info = sheet_config.get(col, {})
                selected = col_info.get("selected", False)

                var = tk.BooleanVar(value=selected)  # Variable pour la case à cocher
                key = (loaded_file.path, sheet.name, col)  # Clé unique pour cette colonne
                self.controller.data_manager.column_vars[key] = var

                def on_toggle(k=key, v=var):
                    """ Gère le basculement de la sélection des colonnes. """
                    if self.controller and self.controller.data_manager:
                        # Si la colonne est sélectionnée, on l'ajoute dans les métadonnées, sinon on la retire
                        if not hasattr(self.controller.data_manager, 'sheet_column_metadata'):
                            self.controller.data_manager.sheet_column_metadata = {}
                        if v.get():
                            self.controller.data_manager.sheet_column_metadata[k] = {"selected": True}
                            print(type(self.controller.data_manager))
                            print(f"{self.controller.data_manager.sheet_column_metadata[k]}")
                            print(f"[✓] Colonne activée: {k}")
                        else:
                            self.controller.data_manager.sheet_column_metadata.pop(k, None)
                            print(f"[✗] Colonne désactivée: {k}")

                # Suivi de la variable de la case à cocher pour gérer l'état
                var.trace_add("write", lambda *args, k=key, v=var: on_toggle(k, v))

                cb = tk.Checkbutton(row_frame, text=col, variable=var)  # Crée une case à cocher pour la colonne
                cb.pack(side="left")

    def save_and_continue(self):
        """ Sauvegarde les métadonnées des colonnes sélectionnées dans un fichier JSON. """
        filepath = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON Files", "*.json")])
        if not filepath:
            return
        # Appel à la méthode save_state du DataManager pour sauvegarder l'état
        self.controller.data_manager.save_state(filepath)

    def load_previous_config(self):
        """ Charge une configuration précédente à partir d'un fichier JSON. """
        filepath = filedialog.askopenfilename(filetypes=[("JSON Files", "*.json")])
        if not filepath:
            return
        try:
            # 1. Charger l'état via DataManager
            self.controller.data_manager.load_state(filepath)
            print(f"Configuration chargée depuis {filepath}")

            # 2. Afficher chaque fichier rechargé
            for loaded_file in self.controller.data_manager.files:
                # On passe un dictionnaire par feuille contenant les colonnes sélectionnées
                config_for_file = {}
                for sheet in loaded_file.sheets:
                    config_for_file[sheet.name] = {}

                    for col in sheet.dataframe.columns:
                        key = (loaded_file.path, sheet.name, col)
                        if key in self.controller.data_manager.sheet_column_metadata:
                            config_for_file[sheet.name][col] = self.controller.data_manager.sheet_column_metadata[key]

                # 3. Appeler display_file avec la config
                self.display_file(loaded_file, config_for_file)

        except Exception as e:
            print(f"Erreur lors du chargement : {e}")

