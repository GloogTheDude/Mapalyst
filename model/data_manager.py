import json
import logging
from .extractor import Extractor
from .data_link import DataLink
import ast
class DataManager:
    def __init__(self):
 
        self.files = []
        self.data_links = []
        self.extractor = Extractor()
        self.sheet_column_metadata={}
        self.zip_column = None
        self.role_columns = {}  # Dict[str (role_name) → Tuple[path, sheet, col]]
        self.group_names = {}  # {node_tuple: nom_de_groupe}

        self.file_frames = {}  # Dictionnaire pour garder une trace des fichiers chargés
        self.column_vars = {}  # Dictionnaire pour garder une trace des cases à cocher des colonnes

    def add_file(self, path: str):
        file = self.extractor.create_file(path)
        self.files.append(file)

    def add_link(self, link: DataLink):
        self.data_links.append(link)

    def load_state(self, filepath):
        """ Charge l'état du DataManager depuis un fichier JSON réduit (sans 'files'). """
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                state = json.load(f)

            # --- 1. Recharger les métadonnées des colonnes
            raw_metadata = state.get('sheet_column_metadata', {})
            self.sheet_column_metadata = {
                ast.literal_eval(key): value for key, value in raw_metadata.items()
            }

            # --- 2. Reconstituer les fichiers à partir des chemins dans les métadonnées
            loaded_paths = set()
            for (path, sheet, col) in self.sheet_column_metadata.keys():
                if path not in loaded_paths:
                    file = self.extractor.create_file(path)
                    self.files.append(file)
                    loaded_paths.add(path)

            # --- 3. Recharger les liens FK
            self.data_links = state.get("data_links", [])

            # --- 4. Recharger les colonnes rôle
            raw_roles = state.get("role_columns", {})
            self.role_columns = {
                role: tuple(value) for role, value in raw_roles.items()
            }

            # --- 5. Recharger la colonne ZIP
            zip_raw = state.get("zip_column", None)
            self.zip_column = tuple(zip_raw) if zip_raw else None

            # --- 6. Recharger les noms de groupes FK
            raw_group_names = state.get("group_names", {})
            self.group_names = {
                ast.literal_eval(k): v for k, v in raw_group_names.items()
            }

            print(f"État chargé depuis {filepath}")
        except Exception as e:
            print(f"Erreur lors du chargement de l'état depuis {filepath}: {e}")



    # Nouvelle fonction pour sauvegarder l'état dans un fichier JSON
    def save_state(self, filepath):
        """ Sauvegarde l'état du DataManager dans un fichier JSON. """
        state = {
            #'files': [file.to_dict() for file in self.files],  # Sérialisation propre de fichiers
            'sheet_column_metadata': {
                str(key): value for key, value in self.sheet_column_metadata.items()
            },  # Clés tuple converties en chaînes
            'data_links': self.data_links,  # DataLink en dict
            'group_names': {
                str(key): value for key, value in self.group_names.items()
            },
            'zip_column': self.zip_column,
            'role_columns': {role: value for role, value in self.role_columns.items()}
        }
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(state, f, indent=2, ensure_ascii=False)
            print(f"État sauvegardé dans {filepath}")
        except Exception as e:
            print(f"Erreur lors de la sauvegarde de l'état dans {filepath}: {e}")

