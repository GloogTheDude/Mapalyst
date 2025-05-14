import tkinter as tk
from tkinter import filedialog

class FileLoaderWindow(tk.Frame):
    def __init__(self, master, controller):
        super().__init__(master)
        self.controller = controller
        self.load_button = tk.Button(self, text="Charger fichier", command=self.load_file)
        self.load_button.pack()

    def load_file(self):
        path = filedialog.askopenfilename(filetypes=[("Excel files", "*.xlsx *.xls")])
        if path:
            self.controller.load_file(path)

    def update_file_list(self, files):
        print("Fichiers chargés:", [f.path for f in files])
