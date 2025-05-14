import tkinter as tk
from tkinter import simpledialog, messagebox, ttk
import uuid
from model.user import TeamMate, Role

DEFAULT_ROLE_NAME = "</NA>"

class AddRoleWindow(tk.Toplevel):
    def __init__(self, master, user_window):
        super().__init__(master)
        self.title("Ajouter un rôle")
        self.user_window = user_window

        tk.Label(self, text="Nom du rôle:").pack(padx=10, pady=5)
        self.role_var = tk.StringVar()
        tk.Entry(self, textvariable=self.role_var).pack(padx=10)

        btn_frame = tk.Frame(self)
        btn_frame.pack(pady=10)
        tk.Button(btn_frame, text="Ajouter", command=self.add_role).pack(side="left", padx=5)
        tk.Button(btn_frame, text="Annuler", command=self.destroy).pack(side="left", padx=5)

    def add_role(self):
        name = self.role_var.get().strip()
        if name:
            role = Role(name)
            self.user_window.controller.user.roles.append(role)
            self.user_window.update_role_menu_all()
            self.destroy()

class DeleteRoleWindow(tk.Toplevel):
    def __init__(self, master, user_window):
        super().__init__(master)
        self.title("Supprimer un rôle")
        self.user_window = user_window

        for role in self.user_window.controller.user.roles:
            if role.name == DEFAULT_ROLE_NAME:
                continue
            frame = tk.Frame(self)
            frame.pack(fill="x", padx=10, pady=2)
            tk.Label(frame, text=role.name).pack(side="left")
            tk.Button(frame, text="Supprimer", command=lambda r=role: self.delete_role(r)).pack(side="right")

    def delete_role(self, role):
        self.user_window.controller.user.roles = [r for r in self.user_window.controller.user.roles if r.name != role.name]
        for mate in self.user_window.controller.user.team_mates:
            if mate.role.name == role.name:
                mate.role = Role(DEFAULT_ROLE_NAME)
        self.user_window.update_teammates()
        self.user_window.update_role_menu_all()
        self.user_window.controller.user.force_save()
        self.destroy()
        DeleteRoleWindow(self.master, self.user_window)

class AddTeamMateWindow(tk.Toplevel):
    def __init__(self, master, user_window, existing_mate=None):
        super().__init__(master)
        self.title("Modifier un teammate" if existing_mate else "Ajouter un teammate")
        self.user_window = user_window
        self.existing_mate = existing_mate

        tk.Label(self, text="Prénom:").pack(padx=10, pady=2)
        self.first_name_var = tk.StringVar(value=existing_mate.first_name if existing_mate else "")
        tk.Entry(self, textvariable=self.first_name_var).pack(padx=10)

        tk.Label(self, text="Nom:").pack(padx=10, pady=2)
        self.last_name_var = tk.StringVar(value=existing_mate.last_name if existing_mate else "")
        tk.Entry(self, textvariable=self.last_name_var).pack(padx=10)

        tk.Label(self, text="ID(s) (séparés par des virgules):").pack(padx=10, pady=2)
        ids_str = ", ".join(existing_mate.ids) if existing_mate else str(uuid.uuid4())
        self.ids_var = tk.StringVar(value=ids_str)
        tk.Entry(self, textvariable=self.ids_var).pack(padx=10)

        tk.Label(self, text="Rôle:").pack(padx=10, pady=2)
        self.role_var = tk.StringVar()
        self.role_menu = ttk.Combobox(self, textvariable=self.role_var, state="readonly")
        self.role_menu.pack(padx=10)

        btn_frame = tk.Frame(self)
        btn_frame.pack(pady=10)
        action_label = "Modifier" if existing_mate else "Ajouter"
        tk.Button(btn_frame, text=action_label, command=self.save_teammate).pack(side="left", padx=5)
        tk.Button(btn_frame, text="Ajouter un rôle", command=self.open_add_role).pack(side="left", padx=5)
        tk.Button(btn_frame, text="Annuler", command=self.destroy).pack(side="left", padx=5)

        self.update_role_menu()
        self.user_window._active_role_menus.append(self)

        if existing_mate:
            self.role_var.set(existing_mate.role.name)

    def update_role_menu(self):
        roles = [r.name for r in self.user_window.controller.user.roles if r.name != DEFAULT_ROLE_NAME]
        self.role_menu["values"] = roles
        if roles and not self.role_var.get():
            self.role_menu.current(0)

    def open_add_role(self):
        AddRoleWindow(self, self.user_window)

    def save_teammate(self):
        ids = [s.strip() for s in self.ids_var.get().split(",") if s.strip()]
        first = self.first_name_var.get().strip()
        last = self.last_name_var.get().strip()
        role_name = self.role_var.get().strip()
        if not ids or not first or not last or not role_name:
            messagebox.showwarning("Champs manquants", "Tous les champs doivent être remplis et un rôle valide doit être sélectionné.")
            return

        role = next((r for r in self.user_window.controller.user.roles if r.name == role_name), Role(DEFAULT_ROLE_NAME))

        if self.existing_mate:
            self.existing_mate.first_name = first
            self.existing_mate.last_name = last
            self.existing_mate.ids = ids
            self.existing_mate.role = role
        else:
            mate = TeamMate(ids=ids, first_name=first, last_name=last, role=role)
            self.user_window.controller.user.team_mates.append(mate)

        self.user_window.update_teammates()
        self.destroy()

class UserWindow(tk.Frame):
    def __init__(self, master, controller):
        super().__init__(master)
        self.controller = controller
        if not hasattr(self, '_active_role_menus'):
            self._active_role_menus = []

        tk.Label(self, text="User Info").grid(row=0, column=0, columnspan=3)

        self.name_var = tk.StringVar()
        self.email_var = tk.StringVar()
        tk.Label(self, text="Nom:").grid(row=1, column=0)
        name_entry = tk.Entry(self, textvariable=self.name_var)
        name_entry.grid(row=1, column=1, columnspan=2)

        tk.Label(self, text="Email:").grid(row=2, column=0)
        email_entry = tk.Entry(self, textvariable=self.email_var)
        email_entry.grid(row=2, column=1, columnspan=2)

        self.teammates_tree = ttk.Treeview(self, columns=("first", "last", "role", "ids"), show="headings")
        self.teammates_tree.heading("first", text="Prénom")
        self.teammates_tree.heading("last", text="Nom")
        self.teammates_tree.heading("role", text="Rôle")
        self.teammates_tree.heading("ids", text="Identifiants")
        self.teammates_tree.grid(row=3, column=0, columnspan=3, sticky="nsew")

        tk.Button(self, text="Ajouter", command=self.add_teammate).grid(row=4, column=0)
        tk.Button(self, text="Modifier", command=self.edit_selected).grid(row=4, column=1)
        tk.Button(self, text="Supprimer", command=self.remove_selected).grid(row=4, column=2)
        tk.Button(self, text="Sauvegarder", command=self.force_save_user).grid(row=5, column=0, columnspan=3, pady=5)
        tk.Button(self, text="Supprimer un rôle", command=self.open_delete_role).grid(row=6, column=0, columnspan=3, pady=2)

    def init_data(self):
        if not any(r.name == DEFAULT_ROLE_NAME for r in self.controller.user.roles):
            self.controller.user.roles.append(Role(DEFAULT_ROLE_NAME))
        self.update_user_info()
        self.update_teammates()

    def update_user_info(self):
        user = self.controller.user
        self.name_var.set(user.name)
        self.email_var.set(user.email)

    def update_teammates(self):
        self.teammates_tree.delete(*self.teammates_tree.get_children())
        for mate in self.controller.user.team_mates:
            self.teammates_tree.insert("", "end", values=(
                mate.first_name, mate.last_name, mate.role.name, ", ".join(mate.ids)
            ))

    def get_selected_teammate(self):
        selected = self.teammates_tree.selection()
        if selected:
            values = self.teammates_tree.item(selected[0])["values"]
            if values:
                for mate in self.controller.user.team_mates:
                    if mate.first_name == values[0] and mate.last_name == values[1] and ", ".join(mate.ids) == values[3]:
                        return mate
        return None

    def remove_selected(self):
        selected = self.teammates_tree.selection()
        if selected:
            values = self.teammates_tree.item(selected[0])["values"]
            if values:
                all_ids = values[3].split(", ")
                self.controller.user.team_mates = [m for m in self.controller.user.team_mates if not any(id_ in m.ids for id_ in all_ids)]
        self.update_teammates()

    def add_teammate(self):
        AddTeamMateWindow(self, self)

    def edit_selected(self):
        mate = self.get_selected_teammate()
        if mate:
            AddTeamMateWindow(self, self, existing_mate=mate)

    def update_role_menu_all(self):
        still_active = []
        for win in self._active_role_menus:
            try:
                if win.winfo_exists():
                    win.update_role_menu()
                    still_active.append(win)
            except tk.TclError:
                continue
        self._active_role_menus = still_active

    def force_save_user(self):
        self.controller.user.name = self.name_var.get().strip()
        self.controller.user.email = self.email_var.get().strip()
        self.controller.user.force_save()

    def open_delete_role(self):
        DeleteRoleWindow(self, self)

