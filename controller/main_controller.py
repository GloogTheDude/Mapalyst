# controller/main_controller.py

import json
from pathlib import Path
from model.user import User
from model.data_manager import DataManager

class MainController:
    def __init__(self, user=None, data_manager=None, main_window=None):
        self.user = user or self.load_user()
        if data_manager: self.data_manager = data_manager
        else: self.data_manager = DataManager()
        self.main_window = main_window

    def set_main_window(self, main_window):
        self.main_window = main_window

    def load_user(self, path="user_data.json"):
        if Path(path).exists():
            try:
                with open(path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    return User.from_dict(data)
            except Exception as e:
                print(f"Erreur lors du chargement du fichier utilisateur : {e}")
        # Utilisateur par défaut
        return User(id="1", name="Admin", email="admin@example.com")

    def save_user(self, path="user_data.json"):
        try:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(self.user.to_dict(), f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Erreur lors de la sauvegarde du fichier utilisateur : {e}")
