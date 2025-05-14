# main.py
from controller.main_controller import MainController
from model.user import User
from model.data_manager import DataManager
from view.main_window import MainWindow

def main():
    # Création du modèle utilisateur (en réalité, il devrait être chargé depuis un JSON)
    user = User(id="1", name="Admin", email="admin@example.com")

    # Création du gestionnaire de données
    data_manager = DataManager()

    # Lancement de la vue principale
    app = MainWindow(controller=None)  # Création de l'interface
    controller = MainController(user, data_manager, app)  # Création du contrôleur

    # On rattache le contrôleur à la vue maintenant qu’il existe
    app.controller = controller

    # Boucle principale Tkinter
    app.mainloop()

if __name__ == "__main__":
    main()
