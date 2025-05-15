import pandas as pd


class Formator():
    
    def __init__(self, path, sheet):
        self.df = pd.read_excel(path, sheet_name=sheet)
            
    def get_tableau_compte(self, group_by_col, count_col):
        return self.df.groupby(group_by_col)[count_col].count().reset_index()

        
    def get_min_max_tableau_compte(self, col, tableau):
        max = tableau[col].max()
        min = tableau[col].min()
        return min, max
        