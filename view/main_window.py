# view/main_window.py
import tkinter as tk
from view.file_loader_window import FileLoaderWindow
from view.data_manager_window import DataManagerWindow
from view.map_drawer import MapDrawer

class MainWindow(tk.Tk):
    def __init__(self, controller):
        super().__init__()
        self.title("Mapalyst")
        self.controller = controller

        self.file_loader = FileLoaderWindow(self, controller)
        self.file_loader.pack(side="left", fill="both", expand=True)

        self.data_manager = DataManagerWindow(self, controller)
        self.data_manager.pack(side="left", fill="both", expand=True)

        self.map_drawer = MapDrawer(self, controller)
        self.map_drawer.pack(side="left", fill="both", expand=True)

    def update_file_list(self, files):
        self.file_loader.update_file_list(files)