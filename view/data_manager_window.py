import tkinter as tk
from tkinter import ttk, simpledialog
from model.extractor import Extractor
import os

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

class DataManagerWindow(tk.Frame):
    def __init__(self, master, controller):
        super().__init__(master)
        self.controller = controller
        self.extractor = Extractor()
        self.foreign_key_links = []
        self.group_names = {}  # node -> group name
        self.zip_column = None
        self.role_column = None

        layout = tk.PanedWindow(self, orient="horizontal", sashrelief="raised", sashwidth=5, bg="#cce6ff")
        layout.pack(fill="both", expand=True)

        self.main_frame = tk.Frame(layout)
        layout.add(self.main_frame, stretch="always")

        self.sidebar_frame = tk.Frame(layout, width=200)
        layout.add(self.sidebar_frame)

        refresh_btn = tk.Button(self.sidebar_frame, text="🔄 Rafraîchir", command=self.refresh_columns)
        refresh_btn.pack(pady=10, padx=10, anchor="n")

        self.group_display = tk.Text(self.sidebar_frame, height=30, state="disabled", wrap="none")
        self.group_display.pack(fill="both", expand=True, padx=10, pady=(0, 10))

    def set_controller(self, controller):
        self.controller = controller
        self.refresh_columns()

    def build_fk_groups(self):
        parent = {}

        def find(x):
            while parent[x] != x:
                parent[x] = parent[parent[x]]
                x = parent[x]
            return x

        def union(x, y):
            root_x = find(x)
            root_y = find(y)
            if root_x != root_y:
                parent[root_y] = root_x

        nodes = set()
        for link in self.foreign_key_links:
            nodes.add(link["from"])
            nodes.add(link["to"])

        for node in nodes:
            parent[node] = node

        for link in self.foreign_key_links:
            union(link["from"], link["to"])

        groups = {}
        for node in nodes:
            root = find(node)
            groups.setdefault(root, []).append(node)

        return groups

    def update_fk_group_display(self):
        self.group_display.configure(state="normal")
        self.group_display.delete("1.0", tk.END)

        groups = self.build_fk_groups()
        if not groups:
            self.group_display.insert(tk.END, "Aucune relation FK définie.\n")
        else:
            for root, items in groups.items():
                name = next((self.group_names.get(n, "Sans nom") for n in items if n in self.group_names), "Sans nom")
                self.group_display.insert(tk.END, f"Groupe '{name}' :\n")
                for item in items:
                    self.group_display.insert(tk.END, f"  - {os.path.basename(item[0])} | {item[1]} | {item[2]}\n")
                self.group_display.insert(tk.END, "\n")

        if self.zip_column:
            self.group_display.insert(tk.END, f"Colonne ZIP : {os.path.basename(self.zip_column[0])} | {self.zip_column[1]} | {self.zip_column[2]}\n")
        if self.role_column:
            self.group_display.insert(tk.END, f"Colonne Rôle : {os.path.basename(self.role_column[0])} | {self.role_column[1]} | {self.role_column[2]}\n")

        self.group_display.configure(state="disabled")

    def refresh_columns(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()

        if not self.controller or not hasattr(self.controller, 'data_manager'):
            print("Controller or data_manager missing")
            return

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
        row = tk.Frame(frame)
        row.pack(fill="x", padx=5, pady=2)

        tk.Label(row, text=col, width=30, anchor="w").grid(row=0, column=0)

        type_var = tk.StringVar()
        type_menu = ttk.Combobox(row, textvariable=type_var,
                                 values=["", "ZIP", "FK", "ROLE", "COUNT", "SUM", "GROUPBY"],
                                 state="readonly", width=10)
        type_menu.grid(row=0, column=1)

        sheet_var = tk.StringVar()
        column_var = tk.StringVar()

        menu1 = ttk.Combobox(row, textvariable=sheet_var, state="disabled", width=30)
        menu2 = ttk.Combobox(row, textvariable=column_var, state="disabled", width=30)

        menu1.grid(row=0, column=2, padx=5)
        menu2.grid(row=0, column=3, padx=5)

        def confirm_link():
            if type_var.get() == "FK" and sheet_var.get() and column_var.get():
                source = (path, sheet, col)
                try:
                    target_sheet = eval(sheet_var.get())
                except:
                    print("Erreur d'analyse de la feuille cible")
                    return
                target = (*target_sheet, column_var.get())

                already_exists = any(
                    (link["from"], link["to"]) == (source, target) or (link["from"], link["to"]) == (target, source)
                    for link in self.foreign_key_links
                )

                if not already_exists:
                    self.foreign_key_links.append({"from": source, "to": target})
                    self.foreign_key_links.append({"from": target, "to": source})

                    known_name = next((self.group_names.get(n) for n in [source, target] if n in self.group_names), None)
                    if not known_name:
                        name = simpledialog.askstring("Nom du groupe", f"Nom pour le groupe contenant {source} et {target} :")
                        if name:
                            self.group_names[source] = name
                            self.group_names[target] = name
                    else:
                        self.group_names[source] = known_name
                        self.group_names[target] = known_name

                print(f"Lien FK entre {source} et {target}")
                self.refresh_columns()

            elif type_var.get() == "ZIP":
                self.zip_column = (path, sheet, col)
                self.refresh_columns()

            elif type_var.get() == "ROLE":
                self.role_column = (path, sheet, col)
                self.refresh_columns()

        link_btn = tk.Button(row, text="Lier", command=confirm_link)
        link_btn.grid(row=0, column=4, padx=5)

        def type_changed(*args):
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
        self.fk_vars.append((sheet_var, column_var, menu1, menu2, (path, sheet)))