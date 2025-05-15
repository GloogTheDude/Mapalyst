
import pandas as pd

class ColumnMetadata:
    def __init__(self, is_zip_code=False, is_foreign_key=False, linked_role=None, map_type="NONE"):
        self.is_zip_code = is_zip_code
        self.is_foreign_key = is_foreign_key
        self.linked_role = linked_role  # Role object or string ID
        self.map_type = map_type  # "COUNT", "SUM", or "NONE"

class Sheet:
    def __init__(self, name: str, dataframe: pd.DataFrame):
        self.name = name
        self.dataframe = dataframe
        self.column_flags = {}  # Dict[str, ColumnMetadata]

    def set_column_flag(self, column_name: str, metadata: ColumnMetadata):
        self.column_flags[column_name] = metadata

class Loaded_File:
    def __init__(self, path: str, sheets: list):
        self.path = path
        self.sheets = sheets  # List[Sheet]