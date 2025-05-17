from .extractor import Extractor
from .data_link import DataLink

class DataManager:
    def __init__(self):
        self.files = []
        self.data_links = []
        self.extractor = Extractor()
        self.file_frames = {}  # Dictionnaire pour garder une trace des fichiers chargés
        self.column_vars = {}  # Dictionnaire pour garder une trace des cases à cocher des colonnes

    def add_file(self, path: str):
        file = self.extractor.create_file(path)
        self.files.append(file)

    def add_link(self, link: DataLink):
        self.data_links.append(link)