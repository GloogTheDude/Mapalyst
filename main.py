from model.user import User, USER_FILE_PATH
from model.data_manager import DataManager
from view.main_window import MainWindow
from controller.main_controller import MainController

def main():
    # Charger l'utilisateur depuis le fichier s'il existe
    user = User.load_from_file(USER_FILE_PATH)
    if user is None:
        user = User(id="1", name="Admin", email="admin@example.com")

    data_manager = DataManager()

    # Crée la fenêtre principale sans contrôleur (il sera injecté après)
    app = MainWindow(controller=None)

    # Crée le contrôleur et connecte-le aux éléments
    controller = MainController(user, data_manager, app)

    # Injecte le contrôleur dans la vue et initialise les données
    app.controller = controller
    app.user_window.controller = controller
    app.user_window.init_data()

    # Lance l'application
    app.mainloop()

if __name__ == "__main__":
    main()
