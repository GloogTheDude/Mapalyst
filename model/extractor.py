import pandas as pd
from .file_model import Loaded_File, Sheet

class Extractor:
    def create_file(self, path: str) -> Loaded_File:
        xls = pd.ExcelFile(path)
        sheets = [Sheet(name, xls.parse(name)) for name in xls.sheet_names]
        return Loaded_File(path, sheets)