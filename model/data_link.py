class DataLink:
    def __init__(self, source_file, source_sheet, source_column, target_file, target_sheet, target_column):
        self.source_file = source_file
        self.source_sheet = source_sheet
        self.source_column = source_column
        self.target_file = target_file
        self.target_sheet = target_sheet
        self.target_column = target_column