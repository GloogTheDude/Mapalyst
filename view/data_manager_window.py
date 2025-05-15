import tkinter as tk
from tkinter import ttk
from model.extractor import Extractor

class DataManagerWindow(tk.Frame):
    def __init__(self, master, controller):
        super().__init__(master)
        self.controller = controller
        self.extractor = Extractor()
        self.foreign_key_links = {}  # (file, sheet, column) : [linked columns]

        tk.Label(self, text="Champs sélectionnés et assignation FK", font=("Arial", 12)).pack(pady=5)

        refresh_btn = tk.Button(self, text="🔄 Rafraîchir", command=self.refresh_columns)
        refresh_btn.pack(pady=(0, 10))

        self.main_frame = tk.Frame(self)
        self.main_frame.pack(fill="both", expand=True)

        self.rows = []

    def set_controller(self, controller):
        self.controller = controller
        self.refresh_columns()

    def refresh_columns(self):
        print("=== METADATA SYNC TEST ===")
        metadata = getattr(self.controller.data_manager, "sheet_column_metadata", {})
        print("Nombre de colonnes reçues :", len(metadata))
        print("Exemples :")
        for i, key in enumerate(metadata.keys()):
            print(" -", key)
            if i >= 2:
                break

        for widget in self.main_frame.winfo_children():
            widget.destroy()
        self.rows.clear()

        header = tk.Frame(self.main_frame)
        header.pack(fill="x", padx=5)
        tk.Label(header, text="Nom de la colonne", width=60, anchor="w", font=("Arial", 10, "bold")).grid(row=0, column=0, sticky="w")
        tk.Label(header, text="Catégorie", width=15, font=("Arial", 10, "bold")).grid(row=0, column=1)
        tk.Label(header, text="Lier à", width=50, font=("Arial", 10, "bold")).grid(row=0, column=2)
        tk.Label(header, text="Action", width=15, font=("Arial", 10, "bold")).grid(row=0, column=3)

        aggregation_types = ["COUNT", "SUM", "GROUPBY"]
        fk_columns = []

        # Collecte des colonnes FK valides
        for (path, sheet, col), widgets in metadata.items():
            if widgets["var"].get() and widgets["combo"].get() == "FK":
                fk_columns.append(f"{path} | {sheet} | {col}")

        for (path, sheet, col), widgets in metadata.items():
            if not widgets["var"].get():
                continue

            selected_type = widgets["combo"].get()
            full_id = f"{path} | {sheet} | {col}"
            cat = selected_type if selected_type in aggregation_types + ["ZIP", "FK", "ROLE"] else "?"

            row = tk.Frame(self.main_frame)
            row.pack(fill="x", padx=5, pady=2)

            tk.Label(row, text=full_id, width=60, anchor="w").grid(row=0, column=0, sticky="w")
            tk.Label(row, text=cat, width=15).grid(row=0, column=1)

            fk_var = tk.StringVar()
            fk_menu = ttk.Combobox(row, values=fk_columns, textvariable=fk_var, width=50, state="readonly")
            fk_menu.grid(row=0, column=2)

            def make_link(src=full_id, var=fk_var):
                tgt = var.get()
                if tgt and tgt != src:
                    self.foreign_key_links.setdefault(src, []).append(tgt)
                    self.foreign_key_links.setdefault(tgt, []).append(src)
                    print(f"Lien établi entre {src} et {tgt}")
                    self.refresh_columns()

            tk.Button(row, text="Lier", command=make_link).grid(row=0, column=3)

            self.rows.append((full_id, cat, fk_var))
