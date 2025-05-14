import tkinter as tk

class DataManagerWindow(tk.Frame):
    def __init__(self, master, controller):
        super().__init__(master)
        self.controller = controller
        tk.Label(self, text="Data Manager").pack()