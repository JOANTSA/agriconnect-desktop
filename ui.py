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
        QWidget {background-color: #fdf6e3; font-family: Arial; font-size: 11pt;}
        QLabel {font-weight: bold; font-size: 12pt;}
        QLineEdit {border: 2px solid #ccc; border-radius: 5px; padding: 6px;}
        QPushButton {background-color: #2e7d32; color: white; border-radius: 5px; padding: 6px 12px; font-weight: bold;}
        QPushButton:hover {background-color: #388e3c;}
        QPushButton#logout {background-color: #c62828;}
        QPushButton#logout:hover {background-color: #d32f2f;}
        QTableWidget {background-color: #fff; border: 1px solid #ccc; gridline-color: #ccc;}
        QHeaderView::section {background-color: #81c784; padding: 4px; border: 1px solid #ccc;}
        """)

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        self.init_login()

    # ---------------- LOGIN ----------------
    def init_login(self):
        self.clear_layout()
        # Header avec logo
        header_layout = QHBoxLayout()
        title = QLabel("Connexion Admin")
        title.setStyleSheet("font-size:16pt;")
        logo = QLabel()
        pixmap = QPixmap("assets/logo.png").scaled(80,80, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        logo.setPixmap(pixmap)
        header_layout.addWidget(title)
        header_layout.addStretch()
        header_layout.addWidget(logo)
        self.layout.addLayout(header_layout)

        self.username_input = QLineEdit(); self.username_input.setPlaceholderText("Email")
        self.password_input = QLineEdit(); self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setPlaceholderText("Mot de passe")
        self.login_btn = QPushButton("Login")
        self.login_btn.clicked.connect(self.do_login)

        self.layout.addWidget(self.username_input)
        self.layout.addWidget(self.password_input)
        self.layout.addWidget(self.login_btn)

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

        self.layout.addLayout(header_layout)

        # Onglets
        self.tabs = QTabWidget()
        self.layout.addWidget(self.tabs)

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
        while self.layout.count():
            child = self.layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

