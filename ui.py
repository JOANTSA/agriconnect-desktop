from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QTabWidget, QTableWidget, QTableWidgetItem, QMessageBox, QHeaderView, QComboBox, QMenu
)
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtCore import Qt
import sys
from api import login, get_producteurs, valider_producteur, refuser_producteur, logout
import requests
from settings import BASE_URL

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.admin_email = None
        self.setWindowTitle("Agriconnect")
        self.resize(1000, 600)

        self.setStyleSheet("""
        QWidget {
            background-color: #fdf6e3;
            font-family: 'Arial';
            font-size: 11pt;
            color: #444;
        }
        QLabel {
            font-weight: bold; 
            font-size: 12pt;
        }
        QLineEdit {
            border: 1px solid #ddd;
            border-radius: 8px;
            padding: 10px;
            background-color: #fff;
        }
        QPushButton {
            background-color: #2e7d32;
            color: white;
            border-radius: 8px;
            padding: 10px 20px;
            font-weight: bold;
            font-size: 12pt;
        }
        QPushButton:hover {
            background-color: #388e3c;
        }
        QPushButton#logout {
            background-color: #c62828;
        }
        QPushButton#logout:hover {
            background-color: #d32f2f;
        }
        QTableWidget {
            background-color: #fff; 
            border: 1px solid #ccc; 
            gridline-color: #ccc;
        }
        QHeaderView::section {
            background-color: #81c784;
            padding: 8px;
            border: 1px solid #ccc;
            font-weight: bold;
        }
        #login_title {
            font-size: 24pt;
            font-weight: bold;
            color: #2e7d32;
            margin-bottom: 20px;
        }
        #side_panel {
            background-color: #2e7d32;
            color: #ffffff;
            border-top-left-radius: 10px;
            border-bottom-left-radius: 10px;
        }
        """)

        # Initialisation d'un layout principal qui sera mis à jour
        self.main_layout = QVBoxLayout()
        self.setLayout(self.main_layout)
        self.init_login()

    # ---------------- LOGIN ----------------
    def init_login(self):
        self.clear_layout()
        
        # Le layout pour organiser les deux colonnes (Panneau de gauche + Panneau de droite)
        two_column_layout = QHBoxLayout()
        
        # Panel de gauche (visuel)
        left_panel = QWidget()
        left_panel.setObjectName("side_panel")
        left_panel.setFixedWidth(400)
        left_panel_layout = QVBoxLayout()
        left_panel.setLayout(left_panel_layout)
        
        # Ajout du logo dans le panel de gauche
        logo_label = QLabel()
        pixmap = QPixmap("assets/logo.png").scaled(150, 150, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        logo_label.setPixmap(pixmap)
        logo_label.setAlignment(Qt.AlignCenter)
        
        title_label = QLabel("Agriconnect")
        title_label.setStyleSheet("font-size: 24pt; font-weight: bold; color: #000;")
        title_label.setAlignment(Qt.AlignCenter)
        
        left_panel_layout.addStretch()
        left_panel_layout.addWidget(logo_label)
        left_panel_layout.addWidget(title_label)
        left_panel_layout.addStretch()
        
        two_column_layout.addWidget(left_panel)
        
        # Panel de droite (formulaire de login)
        right_panel = QWidget()
        right_panel_layout = QVBoxLayout()
        right_panel.setLayout(right_panel_layout)
        
        form_layout = QVBoxLayout()
        form_layout.setAlignment(Qt.AlignCenter)

        login_title = QLabel("Connexion Admin")
        login_title.setObjectName("login_title")
        login_title.setAlignment(Qt.AlignCenter)
        
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Email")
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Mot de passe")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.login_btn = QPushButton("Login")
        self.login_btn.clicked.connect(self.do_login)

        form_layout.addWidget(login_title)
        form_layout.addWidget(self.username_input)
        form_layout.addWidget(self.password_input)
        form_layout.addWidget(self.login_btn)
        
        right_panel_layout.addLayout(form_layout)
        two_column_layout.addWidget(right_panel)
        
        # Ajout du layout à deux colonnes au layout principal
        self.main_layout.addLayout(two_column_layout)

    def do_login(self):
        email = self.username_input.text()
        password = self.password_input.text()

        result = login(email, password)
        if "error" in result:
            QMessageBox.critical(self, "Erreur", result["error"])
            return
        
        self.admin_email = email
        self.init_main()

    # ---------------- MAIN WINDOW AVEC LOGO + LOGOUT ----------------
    def init_main(self):
        self.clear_layout()
        # Header avec logo + email + logout
        header_layout = QHBoxLayout()
        
        title = QLabel("Gestion Producteurs")
        title.setStyleSheet("font-size:16pt; font-weight:bold;")
        header_layout.addWidget(title)
        header_layout.addStretch()
        
        # Email affiché
        if self.admin_email:
            lbl_email = QLabel("Bienvenue, "+self.admin_email)
            lbl_email.setStyleSheet("font-size:11pt; color:#444; margin-right:10px;")
            header_layout.addWidget(lbl_email)
          
        # Logo  
        logo = QLabel()
        pixmap = QPixmap("assets/logo.png").scaled(80,80, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        logo.setPixmap(pixmap)
        header_layout.addWidget(logo)

        # Bouton logout
        logout_btn = QPushButton("Logout")
        logout_btn.setObjectName("logout")
        logout_btn.clicked.connect(self.logout)
        header_layout.addWidget(logout_btn)

        self.main_layout.addLayout(header_layout)

        # Onglets
        self.tabs = QTabWidget()
        self.main_layout.addWidget(self.tabs)

        self.tab_create = QWidget()
        self.tab_list = QWidget()
        self.tabs.addTab(self.tab_create, "Créer Producteur")
        self.tabs.addTab(self.tab_list, "Liste des Producteurs")

        self.init_create_tab()
        self.init_list_tab()

    # ---------------- ONGLET CREATION ----------------
    def init_create_tab(self):
        layout = QVBoxLayout()
        self.tab_create.setLayout(layout)

        self.nom_input = QLineEdit(); self.nom_input.setPlaceholderText("Nom")
        self.prenom_input = QLineEdit(); self.prenom_input.setPlaceholderText("Prénom")
        self.email_input = QLineEdit(); self.email_input.setPlaceholderText("Email")
        self.password_input = QLineEdit(); self.password_input.setPlaceholderText("Mot de passe")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.contact_input = QLineEdit(); self.contact_input.setPlaceholderText("Contact")
        self.adresse_input = QLineEdit(); self.adresse_input.setPlaceholderText("Adresse")

        # Rôle (Producteur ou Acheteur)
        self.role_combobox = QComboBox()
        self.role_combobox.addItems(["Producteur", "Acheteur"])

        self.add_btn = QPushButton("Ajouter Producteur")
        self.add_btn.clicked.connect(self.add_producer)

        layout.addWidget(QLabel("Créer un nouveau producteur"))
        layout.addWidget(self.nom_input)
        layout.addWidget(self.prenom_input)
        layout.addWidget(self.email_input)
        layout.addWidget(self.password_input)
        layout.addWidget(self.contact_input)
        layout.addWidget(self.adresse_input)
        layout.addWidget(QLabel("Rôle"))
        layout.addWidget(self.role_combobox)
        layout.addWidget(self.add_btn)
        layout.addStretch()

    # ---------------- ONGLET LISTE ----------------
    def init_list_tab(self):
        layout = QVBoxLayout()
        self.tab_list.setLayout(layout)

        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(["ID", "Nom", "Prénom", "Contact", "Statut", "Actions"])
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.table)
        self.load_producers()

    def load_producers(self):
        self.table.setRowCount(0)
        data = get_producteurs()
        if not isinstance(data, list):
            QMessageBox.critical(self, "Erreur", str(data))
            return

        for row_num, prod in enumerate(data):
            self.table.insertRow(row_num)
            self.table.setItem(row_num, 0, QTableWidgetItem(str(prod["id"])))
            self.table.setItem(row_num, 1, QTableWidgetItem(prod["nom"]))
            self.table.setItem(row_num, 2, QTableWidgetItem(prod["prenom"]))
            self.table.setItem(row_num, 3, QTableWidgetItem(prod["email"]))
            self.table.setItem(row_num, 4, QTableWidgetItem(prod["statut_validation"]))

            # --- Boutons Actions ---
            btn_actions = QPushButton("⋮")
            btn_actions.setStyleSheet("font-weight: bold; font-size: 14pt;")
            btn_actions.setFixedWidth(40)
        
        
            menu = QMenu()
            action_valider = menu.addAction("Valider")
            action_refuser = menu.addAction("Refuser")
            action_attente = menu.addAction("En attente")
            
            # Connecter les actions
            action_valider.triggered.connect(lambda _, pid=prod["id"]: self.validate_producer(pid))
            action_refuser.triggered.connect(lambda _, pid=prod["id"]: self.refuse_producer(pid))
            action_attente.triggered.connect(lambda _, pid=prod["id"]: self.set_pending(pid))

            # wrapper pour mettre boutons côte à côte
            btn_actions.setMenu(menu)

            self.table.setCellWidget(row_num, 5, btn_actions)

    def validate_producer(self, producer_id):
        res = valider_producteur(producer_id)
        QMessageBox.information(self, "Valider", str(res))
        self.load_producers()

    def refuse_producer(self, producer_id):
        res = refuser_producteur(producer_id)
        QMessageBox.warning(self, "Refuser", str(res))
        self.load_producers()

    def logout(self):
        logout()
        QMessageBox.information(self, "Logout", "Déconnexion réussie")
        self.init_login()
        
    def add_producer(self):
        data = {
            "nom": self.nom_input.text(),
            "prenom": self.prenom_input.text(),
            "email": self.email_input.text(),
            "mot_de_passe": self.password_input.text(),
            "role": self.role_combobox.currentText(),  # "Producteur" ou "Acheteur"
            "contact": self.contact_input.text(),
            "adresse": self.adresse_input.text()
        }

        try:
            response = requests.post(f"{BASE_URL}/auth/register", json=data)
            if response.status_code == 201:
                QMessageBox.information(self, "Succès", "Compte créé avec succès !")
                self.load_producers()  # recharger la liste
            else:
                QMessageBox.warning(self, "Erreur", f"Échec : {response.json().get('message', 'Erreur inconnue')}")
        except Exception as e:
            QMessageBox.critical(self, "Erreur", str(e))



    # ---------------- UTIL ----------------
    def clear_layout(self):
        # Vérifiez que le layout principal a été initialisé
        if not hasattr(self, 'main_layout') or self.main_layout is None:
            return
            
        while self.main_layout.count():
            child = self.main_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
            elif child.layout():
                self.clear_layout_recursively(child.layout())
    
    def clear_layout_recursively(self, layout):
        if layout is not None:
            while layout.count():
                item = layout.takeAt(0)
                widget = item.widget()
                if widget is not None:
                    widget.deleteLater()
                else:
                    self.clear_layout_recursively(item.layout())

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
