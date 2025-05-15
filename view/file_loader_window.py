import tkinter as tk
from tkinter import filedialog, ttk
import os
import json
import pandas as pd
from model.extractor import Extractor

class CollapsibleFrame(ttk.Frame):
    def __init__(self, master, text="", *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.show = tk.BooleanVar(value=True)

        header = ttk.Frame(self)
        header.pack(fill="x")

        self.icon_label = ttk.Label(header, text="▼", width=2)
        self.icon_label.pack(side="left")
        self.icon_label.bind("<Button-1>", lambda e: self.toggle(force_toggle=True))

        self.toggle_button = ttk.Checkbutton(
            header, text=text, style="Toolbutton", variable=self.show, command=self.toggle
        )
        self.toggle_button.pack(side="left", fill="x", expand=True, pady=2)

        self.sub_frame = ttk.Frame(self)
        self.sub_frame.pack(fill="both", expand=True)

    def toggle(self, force_toggle=False):
        if force_toggle:
            self.show.set(not self.show.get())

        if self.show.get():
            self.sub_frame.pack(fill="both", expand=True)
            self.icon_label.configure(text="▼")
        else:
            self.sub_frame.forget()
            self.icon_label.configure(text="▶")

    def get_frame(self):
        return self.sub_frame

class FileLoaderWindow(tk.Frame):
    def __init__(self, master, controller):
        super().__init__(master)
        self.controller = controller
        self.extractor = Extractor()
        self.file_frames = {}
        self.column_vars = {}  # key = (path, sheet, col) -> BooleanVar

        button_frame = tk.Frame(self)
        button_frame.pack(pady=5)

        tk.Button(button_frame, text="Charger des fichiers Excel", command=self.load_file).pack(side="left", padx=5)
        tk.Button(button_frame, text="Ajouter un fichier Excel", command=self.add_file).pack(side="left", padx=5)
        tk.Button(button_frame, text="Sauvegarder et continuer", command=self.save_and_continue).pack(side="left", padx=5)
        tk.Button(button_frame, text="Charger précédent travail", command=self.load_previous_config).pack(side="left", padx=5)

        container_frame = tk.Frame(self)
        container_frame.pack(fill="both", expand=True)

        self.canvas = tk.Canvas(container_frame)
        scrollbar = tk.Scrollbar(container_frame, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas)

        self.scrollable_frame.bind(
            "<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self.scrollable_frame.bind_all("<MouseWheel>", self._on_mousewheel)
        self.scrollable_frame.bind_all("<Button-4>", self._on_mousewheel)
        self.scrollable_frame.bind_all("<Button-5>", self._on_mousewheel)
        self.canvas.bind_all("<Up>", self._on_arrow)
        self.canvas.bind_all("<Down>", self._on_arrow)

    def _on_mousewheel(self, event):
        if event.num == 5 or event.delta < 0:
            self.canvas.yview_scroll(1, "units")
        elif event.num == 4 or event.delta > 0:
            self.canvas.yview_scroll(-1, "units")

    def _on_arrow(self, event):
        if event.keysym == "Down":
            self.canvas.yview_scroll(1, "units")
        elif event.keysym == "Up":
            self.canvas.yview_scroll(-1, "units")

    def set_controller(self, controller):
        self.controller = controller
        if not hasattr(self.controller.data_manager, 'sheet_column_metadata'):
            self.controller.data_manager.sheet_column_metadata = {}

    def load_file(self):
        if not self.controller or not self.controller.data_manager:
            print("Erreur : contrôleur non défini.")
            return

        paths = filedialog.askopenfilenames(filetypes=[("Excel Files", "*.xlsx *.xls")])
        for path in paths:
            self.import_file(path)

    def add_file(self):
        path = filedialog.askopenfilename(filetypes=[("Excel Files", "*.xlsx *.xls")])
        if path:
            self.import_file(path)

    def import_file(self, path, config_for_file=None):
        if path not in self.file_frames:
            loaded_file = self.extractor.create_file(path)
            self.controller.data_manager.files.append(loaded_file)
            self.display_file(loaded_file, config_for_file)

    def display_file(self, loaded_file, config_for_file=None):
        file_frame = CollapsibleFrame(self.scrollable_frame, text=os.path.basename(loaded_file.path))
        file_frame.pack(fill="x", padx=10, pady=5, expand=True)
        self.file_frames[loaded_file.path] = file_frame

        for sheet in loaded_file.sheets:
            sheet_config = config_for_file.get(sheet.name, {}) if config_for_file else {}
            sheet_frame = CollapsibleFrame(file_frame.get_frame(), text=sheet.name)
            sheet_frame.pack(fill="x", padx=10, pady=5)

            for col in sheet.dataframe.columns:
                row_frame = tk.Frame(sheet_frame.get_frame())
                row_frame.pack(fill="x", anchor="w")

                col_info = sheet_config.get(col, {})
                selected = col_info.get("selected", False)

                var = tk.BooleanVar(value=selected)
                key = (loaded_file.path, sheet.name, col)
                self.column_vars[key] = var

                def on_toggle(k=key, v=var):
                    if self.controller and self.controller.data_manager:
                        if not hasattr(self.controller.data_manager, 'sheet_column_metadata'):
                            self.controller.data_manager.sheet_column_metadata = {}
                        if v.get():
                            self.controller.data_manager.sheet_column_metadata[k] = True
                        else:
                            self.controller.data_manager.sheet_column_metadata.pop(k, None)

                var.trace_add("write", lambda *args, k=key, v=var: on_toggle(k, v))

                cb = tk.Checkbutton(row_frame, text=col, variable=var)
                cb.pack(side="left")

    def save_and_continue(self):
        filepath = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON Files", "*.json")])
        if not filepath:
            return
        config = {}
        for key, var in self.column_vars.items():
            path, sheet, column = key
            checked = var.get()
            config.setdefault(path, {}).setdefault(sheet, {})[column] = {"selected": checked, "type": ""}

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        print(f"Paramètres sauvegardés dans {filepath}")

        if hasattr(self.controller, "go_to_next_tab"):
            self.controller.go_to_next_tab()

    def load_previous_config(self):
        filepath = filedialog.askopenfilename(filetypes=[("JSON Files", "*.json")])
        if not filepath:
            return
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                config = json.load(f)

            for path in config:
                loaded_file = self.extractor.create_file(path)
                self.controller.data_manager.files.append(loaded_file)
                self.display_file(loaded_file, config_for_file=config[path])

            print(f"Configuration chargée depuis {filepath}")
        except Exception as e:
            print(f"Erreur lors du chargement : {e}")
