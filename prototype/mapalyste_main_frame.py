import tkinter as tk
from tkinter import ttk 

class MainFrame(tk.Frame):
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.pack() 
        
        self.notebook = ttk.Notebook(self)
        
        self.tab1 = tk.Frame(self.notebook)
        self.tab2 = tk.Frame(self.notebook)
        self.tab3 = tk.Frame(self.notebook)
        
        self.notebook.add(self.tab1,text="File and field selection")
        self.notebook.add(self.tab2,text="Nodes parameters")
        self.notebook.add(self.tab3,text="Graphs")
        
        self.notebook.pack(expand=True, fill="both")
        
        tk.Label(self.tab1, text="File and field selection").pack(padx=20, pady=20)
        tk.Label(self.tab2, text="Nodes parameters").pack(padx=20, pady=20)
        tk.Label(self.tab3, text="Graphs").pack(padx=20, pady=20)
        
        
    


if __name__ == "__main__":
    root = tk.Tk()
    root.title("Tkinter Example")
    root.geometry("600x400")  

    main_frame = MainFrame(root)

    root.mainloop()
