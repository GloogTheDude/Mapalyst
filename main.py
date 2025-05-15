# main.py
from controller.main_controller import MainController
from model.user import User
from model.data_manager import DataManager
from view.main_window import MainWindow

def main():
    # Création du modèle utilisateur (à charger depuis un JSON plus tard)
    user = User.load("user_data.json")

    # Création du gestionnaire de données
    data_manager = DataManager()

    # Création de l’interface graphique principale (vue)
    app = MainWindow(controller=None)
    controller = MainController(user, data_manager, app)
    app.set_controller(controller)  # appelle set_controller sur toutes les fenêtres

    app.user_window.init_data()

    #controller.user.display()
    # Lancement de la boucle Tkinter
    app.mainloop()
    
if __name__ == "__main__":
    main()
