import tkinter as tk
from tkinter import ttk
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
        self.main_frame = tk.Frame(self)
        self.main_frame.pack(fill="both", expand=True)

        refresh_btn = tk.Button(self, text="🔄 Rafraîchir", command=self.refresh_columns)
        refresh_btn.pack(pady=10)

    def set_controller(self, controller):
        self.controller = controller
        if not hasattr(self.controller.data_manager, "foreign_key_links"):
            self.controller.data_manager.foreign_key_links = {}
        self.refresh_columns()

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

        fk_vars = []

        def build_row(frame, path, sheet, col):
            row = tk.Frame(frame)
            row.pack(fill="x", padx=5, pady=2)

            tk.Label(row, text=col, width=30, anchor="w").grid(row=0, column=0)

            type_var = tk.StringVar()
            type_menu = ttk.Combobox(row, textvariable=type_var, values=["", "ZIP", "FK", "ROLE", "COUNT", "SUM", "GROUPBY"], state="readonly", width=10)
            type_menu.grid(row=0, column=1)

            sheet_var = tk.StringVar()
            column_var = tk.StringVar()

            sheet_menu = ttk.Combobox(row, textvariable=sheet_var, state="disabled", width=30)
            column_menu = ttk.Combobox(row, textvariable=column_var, state="disabled", width=30)

            sheet_menu.grid(row=0, column=2, padx=5)
            column_menu.grid(row=0, column=3, padx=5)

            def confirm_link():
                if type_var.get() == "FK" and sheet_var.get() and column_var.get():
                    source = f"{path} | {sheet} | {col}"
                    target = f"{sheet_var.get()} | {column_var.get()}"
                    links = self.controller.data_manager.foreign_key_links
                    links.setdefault(source, []).append(target)
                    links.setdefault(target, []).append(source)
                    print(f"Lien FK entre {source} et {target}")
                    self.refresh_columns()

            link_btn = tk.Button(row, text="Lier", command=confirm_link)
            link_btn.grid(row=0, column=4, padx=5)

            fk_vars.append((sheet_var, column_var, sheet_menu, column_menu, (path, sheet)))

            def type_changed(*args):
                if type_var.get() == "FK":
                    sheet_menu["state"] = "readonly"
                    column_menu["state"] = "readonly"
                else:
                    sheet_menu["state"] = "disabled"
                    column_menu["state"] = "disabled"
                    sheet_var.set("")
                    column_var.set("")

            type_var.trace_add("write", type_changed)

        for (path, sheet), cols in grouped_by_sheet.items():
            section = CollapsibleFrame(self.main_frame, text=f"{sheet} ({os.path.basename(path)})")
            section.pack(fill="x", padx=10, pady=5, expand=True)
            frame = section.get_frame()

            for col in cols:
                build_row(frame, path, sheet, col)

        sheet_keys = list(grouped_by_sheet.keys())
        for sheet_var, column_var, sheet_menu, column_menu, origin in fk_vars:
            other_sheets = [str(k) for k in sheet_keys if k != origin]
            sheet_menu["values"] = other_sheets

            def make_update_options(sv, cv, cm):
                def update_options(*_):
                    try:
                        selected_sheet = eval(sv.get())
                        options = grouped_by_sheet.get(selected_sheet, [])
                    except:
                        options = []
                    cm["values"] = options
                    if options:
                        cv.set(options[0])
                return update_options

            sheet_var.trace_add("write", make_update_options(sheet_var, column_var, column_menu))
