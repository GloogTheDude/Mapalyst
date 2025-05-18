import tkinter as tk
from tkinter import ttk, simpledialog
from model.extractor import Extractor
import os
from utils.ui_elem import CollapsibleFrame


# Classe principale pour gérer la fenêtre de gestion des données
class DataManagerWindow(tk.Frame):
    def __init__(self, master, controller):
        super().__init__(master)
        self.controller = controller  # Le contrôleur qui gère l'application
        self.extractor = Extractor()  # Objet pour extraire les données des fichiers Excel
        self.foreign_key_links = []  # Liste pour stocker les liens FK
        self.group_names = {}  # Dictionnaire pour les noms de groupes associés aux noeuds
        self.zip_column = None  # Colonne ZIP (initialement non définie)
        self.role_column = None  # Colonne rôle (initialement non définie)

        # Création du layout horizontal pour la fenêtre (paned window)
        layout = tk.PanedWindow(self, orient="horizontal", sashrelief="raised", sashwidth=5, bg="#cce6ff")
        layout.pack(fill="both", expand=True)

        # Frame principale pour afficher les éléments
        self.main_frame = tk.Frame(layout)
        layout.add(self.main_frame, stretch="always")

        # Frame latérale pour la gestion des actions
        self.sidebar_frame = tk.Frame(layout, width=200)
        layout.add(self.sidebar_frame)

        # Bouton pour rafraîchir l'affichage
        refresh_btn = tk.Button(self.sidebar_frame, text="🔄 Rafraîchir", command=self.refresh_columns)
        refresh_btn.pack(pady=10, padx=10, anchor="n")

        # Zone de texte pour afficher les groupes
        self.group_display = tk.Text(self.sidebar_frame, height=30, state="disabled", wrap="none")
        self.group_display.pack(fill="both", expand=True, padx=10, pady=(0, 10))

    def set_controller(self, controller):
        """ Définit le contrôleur principal. """
        self.controller = controller
        self.refresh_columns()  # Rafraîchit les colonnes au moment de l'initialisation

    def build_fk_groups(self):
        """ Crée les groupes de liens FK à partir des données. """
        parent = {}

        # Fonction pour trouver le parent d'un noeud (utilisée pour union-find)
        def find(x):
            while parent[x] != x:
                parent[x] = parent[parent[x]]
                x = parent[x]
            return x

        # Fonction pour unir deux noeuds dans le même groupe
        def union(x, y):
            root_x = find(x)
            root_y = find(y)
            if root_x != root_y:
                parent[root_y] = root_x

        # Création des noeuds à partir des liens FK
        nodes = set()
        for link in self.foreign_key_links:
            nodes.add(tuple(link["from"]))
            nodes.add(tuple(link["to"]))


        # Initialisation des groupes pour chaque noeud
        for node in nodes:
            parent[node] = node

        # Union des noeuds selon les liens FK
        for link in self.foreign_key_links:
            union(tuple(link["from"]), tuple(link["to"]))

        # Création des groupes de noeuds
        groups = {}
        for node in nodes:
            root = find(node)
            groups.setdefault(root, []).append(node)

        return groups

    def update_fk_group_display(self):
        """ Met à jour l'affichage des groupes de liens FK dans la fenêtre. """
        self.group_display.configure(state="normal")
        self.group_display.delete("1.0", tk.END)

        # Construction des groupes FK
        groups = self.build_fk_groups()
        if not groups:
            self.group_display.insert(tk.END, "Aucune relation FK définie.\n")
        else:
            for root, items in groups.items():
                # Récupère le nom du groupe
                name = next((self.group_names.get(n, "Sans nom") for n in items if n in self.group_names), "Sans nom")
                self.group_display.insert(tk.END, f"Groupe '{name}' :\n")
                for item in items:
                    # Affiche les éléments du groupe
                    self.group_display.insert(tk.END, f"  - {os.path.basename(item[0])} | {item[1]} | {item[2]}\n")
                self.group_display.insert(tk.END, "\n")

        # Affichage des colonnes ZIP et Rôle, si définies
        if self.zip_column:
            self.group_display.insert(tk.END, f"Colonne ZIP : {os.path.basename(self.zip_column[0])} | {self.zip_column[1]} | {self.zip_column[2]}\n")
        if self.role_columns:
            self.group_display.insert(tk.END, "\nColonnes associées aux rôles :\n")
            for role, (p, s, c) in self.role_columns.items():
                self.group_display.insert(tk.END, f"  - {role} → {os.path.basename(p)} | {s} | {c}\n")


        self.group_display.configure(state="disabled")

    def refresh_columns(self):
        """ Rafraîchit les colonnes et leur affichage dans la fenêtre. """
        print(f"self.controller.data_manager.data_links is {str(self.controller.data_manager.data_links)}")

        # Synchronise les données depuis le DataManager
        self.foreign_key_links = getattr(self.controller.data_manager, "data_links", [])
        self.zip_column = getattr(self.controller.data_manager, "zip_column", None)
        if self.zip_column:
            self.zip_column = tuple(self.zip_column)
        self.role_columns = getattr(self.controller.data_manager, "role_columns", {})
        self.group_names = getattr(self.controller.data_manager, "group_names", {})

        # Réinitialise l'affichage principal
        for widget in self.main_frame.winfo_children():
            widget.destroy()

        if not self.controller or not hasattr(self.controller, 'data_manager'):
            print("Controller or data_manager missing")
            return

        # Récupère les métadonnées de colonnes sélectionnées
        metadata = getattr(self.controller.data_manager, "sheet_column_metadata", {})
        grouped_by_sheet = {}

        for key, info in metadata.items():
            if isinstance(info, dict) and info.get("selected"):
                path, sheet, col = key
                grouped_by_sheet.setdefault((path, sheet), []).append(col)

        if not grouped_by_sheet:
            tk.Label(self.main_frame, text="Aucune colonne sélectionnée.", font=("Arial", 12)).pack(pady=10)
            return

        self.sheet_keys = list(grouped_by_sheet.keys())
        self.fk_vars = []

        for (path, sheet), cols in grouped_by_sheet.items():
            section = CollapsibleFrame(self.main_frame, text=f"{sheet} ({os.path.basename(path)})")
            section.pack(fill="x", padx=10, pady=5, expand=True)
            frame = section.get_frame()

            for col in cols:
                self._build_row(frame, path, sheet, col, grouped_by_sheet)

        self.update_fk_group_display()


    def _build_row(self, frame, path, sheet, col, grouped_by_sheet):
        """ Crée une ligne avec des menus déroulants pour chaque colonne. """
        row = tk.Frame(frame)
        row.pack(fill="x", padx=5, pady=2)

        # Affiche le nom de la colonne
        tk.Label(row, text=col, width=30, anchor="w").grid(row=0, column=0)

        # Menu déroulant pour choisir le type
        type_var = tk.StringVar()
        type_menu = ttk.Combobox(row, textvariable=type_var,
                                 values=["", "ZIP", "FK", "ROLE", "COUNT", "SUM", "GROUPBY"],
                                 state="readonly", width=10)
        type_menu.grid(row=0, column=1)

        # Variables pour les menus déroulants de la feuille et de la colonne
        sheet_var = tk.StringVar()
        column_var = tk.StringVar()

        menu1 = ttk.Combobox(row, textvariable=sheet_var, state="disabled", width=30)
        menu2 = ttk.Combobox(row, textvariable=column_var, state="disabled", width=30)

        menu1.grid(row=0, column=2, padx=5)
        menu2.grid(row=0, column=3, padx=5)

        def confirm_link():
            """ Confirme l'action choisie pour la colonne : FK, ZIP ou ROLE. """
            selected_type = type_var.get()
            source = (path, sheet, col)

            if selected_type == "FK":
                # Vérifie que des valeurs sont sélectionnées
                if not sheet_var.get() or not column_var.get():
                    print("Veuillez sélectionner une feuille et une colonne cibles.")
                    return

                try:
                    target_sheet = eval(sheet_var.get())
                except Exception:
                    print("Erreur d'analyse de la feuille cible.")
                    return

                target = (*target_sheet, column_var.get())

                # Vérifie si le lien FK existe déjà
                already_exists = any(
                    (link["from"], link["to"]) == (source, target) or (link["from"], link["to"]) == (target, source)
                    for link in self.foreign_key_links
                )

                if not already_exists:
                    # Ajoute le lien dans les deux sens
                    self.foreign_key_links.append({"from": source, "to": target})
                    self.foreign_key_links.append({"from": target, "to": source})

                    # Sauvegarde dans DataManager
                    self.controller.data_manager.data_links = self.foreign_key_links
                    print(f"self.controller.data_manager.data_links is now: {str(self.controller.data_manager.data_links)}")

                    # Gestion du nom du groupe FK
                    known_name = next((self.group_names.get(n) for n in [source, target] if n in self.group_names), None)
                    if not known_name:
                        name = simpledialog.askstring(
                            "Nom du groupe",
                            f"Nom pour le groupe contenant :\n - {os.path.basename(source[0])} | {source[1]} | {source[2]}\n - {os.path.basename(target[0])} | {target[1]} | {target[2]}"
                        )
                        if name:
                            self.group_names[source] = name
                            self.group_names[target] = name
                    else:
                        self.group_names[source] = known_name
                        self.group_names[target] = known_name

                    print(f"[✓] Lien FK ajouté entre {source} et {target}")
                else:
                    print("[i] Le lien FK existe déjà.")

                self.refresh_columns()

            elif selected_type == "ZIP":
                self.zip_column = source
                self.controller.data_manager.zip_column = source
                print(f"[✓] Colonne ZIP définie : {source}")
                self.refresh_columns()

            elif selected_type == "ROLE":
                role_name = sheet_var.get()
                if not role_name:
                    print("Aucun rôle sélectionné.")
                    return

                self.role_column = source  # Optionnel si tu veux garder le dernier
                self.controller.data_manager.role_columns[role_name] = source

                print(f"[✓] Rôle '{role_name}' associé à : {source}")
                self.refresh_columns()



        link_btn = tk.Button(row, text="Lier", command=confirm_link)
        link_btn.grid(row=0, column=4, padx=5)

        def type_changed(*args):
            """ Met à jour l'état des menus déroulants lorsque le type change. """
            selected_type = type_var.get()
            if selected_type == "FK":
                menu1["state"] = "readonly"
                menu2["state"] = "readonly"
                menu1["values"] = [str(k) for k in self.sheet_keys if k != (path, sheet)]

                def update_columns(*_):
                    try:
                        selected_sheet = eval(sheet_var.get())
                        columns = grouped_by_sheet.get(selected_sheet, [])
                    except:
                        columns = []
                    menu2["values"] = columns
                    if columns:
                        column_var.set(columns[0])
                sheet_var.trace_add("write", update_columns)

            elif selected_type == "ROLE":
                menu1["state"] = "readonly"
                menu2["state"] = "disabled"
                sheet_var.set("")
                column_var.set("")
                menu1["values"] = [r.name for r in self.controller.user.roles]

            else:
                menu1["state"] = "disabled"
                menu2["state"] = "disabled"
                sheet_var.set("")
                column_var.set("")

        type_var.trace_add("write", type_changed)
        self.fk_vars.append((sheet_var, column_var, menu1, menu2, (path, sheet)))  # Ajoute cette configuration aux variables FK
