import pandas as pd
from typing import Dict

class ColumnMetadata:
    def __init__(self, is_zip_code=False, is_foreign_key=False, linked_role=None, map_type="NONE"):
        self.is_zip_code = is_zip_code
        self.is_foreign_key = is_foreign_key
        self.linked_role = linked_role  # Role object or string ID
        self.map_type = map_type  # "COUNT", "SUM", or "NONE"

    def to_dict(self):
        """ Convertit l'objet ColumnMetadata en dictionnaire pour la sérialisation JSON. """
        return {
            'is_zip_code': self.is_zip_code,
            'is_foreign_key': self.is_foreign_key,
            'linked_role': self.linked_role,
            'map_type': self.map_type
        }

class Sheet:
    def __init__(self, name: str, dataframe: pd.DataFrame):
        self.name = name
        self.dataframe = dataframe  # Pandas DataFrame
        self.column_flags = {}  # Dict[str, ColumnMetadata]

    def set_column_flag(self, column_name: str, metadata: ColumnMetadata):
        """ Associe des métadonnées à une colonne spécifique. """
        self.column_flags[column_name] = metadata

    def to_dict(self):
        """ Convertit un objet Sheet en dictionnaire pour la sérialisation JSON. """
        return {
            'name': self.name,
            'dataframe_columns': list(self.dataframe.columns),  # Sérialise juste les noms de colonnes, pas le DataFrame entier
            'column_flags': {col: metadata.to_dict() for col, metadata in self.column_flags.items()}  # Sérialisation des métadonnées
        }

class Loaded_File:
    def __init__(self, path: str, sheets: list):
        self.path = path
        self.sheets = sheets  # List[Sheet]
        
    def to_dict(self):
        """ Convertit l'objet Loaded_File en dictionnaire pour la sérialisation JSON. """
        return {
            'path': self.path,
            'sheets': [sheet.to_dict() for sheet in self.sheets]  # Sérialisation des objets Sheet
        }
