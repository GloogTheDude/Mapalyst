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

        self.file_loader_window = FileLoaderWindow(self.notebook, None)  # controller injecté plus tard
        self.notebook.add(self.file_loader_window, text="Fichiers")

        self.data_manager = DataManagerWindow(self.notebook, controller)
        self.notebook.add(self.data_manager, text="Données")

        self.map_drawer = MapDrawer(self.notebook)
        self.notebook.add(self.map_drawer, text="Carte")

    def set_controller(self, controller):
        self.controller = controller
        self.user_window.set_controller(controller)
        self.file_loader_window.set_controller(controller)
        self.data_manager.set_controller(controller)
        self.map_drawer.set_controller(controller)  

