class MainController:
    def __init__(self, user, data_manager, main_window):
        self.user = user
        self.data_manager = data_manager
        self.view = main_window

    def load_file(self, path):
        self.data_manager.add_file(path)
        self.view.update_file_list(self.data_manager.files)

    def set_column_flags(self, sheet, column, flags):
        sheet.set_column_flag(column, flags)

    def add_data_link(self, link):
        self.data_manager.add_link(link)