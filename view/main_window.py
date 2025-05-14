import tkinter as tk
from tkinter import ttk
from view.file_loader_window import FileLoaderWindow
from view.data_manager_window import DataManagerWindow
from view.map_drawer import MapDrawer
from view.user_window import UserWindow

class MainWindow(tk.Tk):
    def __init__(self, controller):
        super().__init__()
        self.title("Mapalyst")
        self.controller = controller

        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True)

        self.user_window = UserWindow(self.notebook, None)  # controller injecté plus tard
        self.notebook.add(self.user_window, text="User")

        self.file_loader = FileLoaderWindow(self.notebook, controller)
        self.notebook.add(self.file_loader, text="Fichiers")

        self.data_manager = DataManagerWindow(self.notebook, controller)
        self.notebook.add(self.data_manager, text="Données")

        self.map_drawer = MapDrawer(self.notebook, controller)
        self.notebook.add(self.map_drawer, text="Carte")

    def update_file_list(self, files):
        self.file_loader.update_file_list(files)
