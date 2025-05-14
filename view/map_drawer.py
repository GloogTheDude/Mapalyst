import tkinter as tk

class MapDrawer(tk.Frame):
    def __init__(self, master, controller):
        super().__init__(master)
        self.controller = controller
        tk.Label(self, text="Map Drawer").pack()
        