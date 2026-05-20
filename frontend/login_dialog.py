from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox
)
from PyQt6.QtCore import Qt
from datetime import datetime
from backend.database import SessionLocal
from backend.auth import authenticate_user

class LoginDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Вход в систему")
        self.setModal(True)
        self.setFixedSize(400, 200)
        self.current_user = None
        self.db = SessionLocal()
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()

        phone_label = QLabel("Номер телефона:")
        self.phone_input = QLineEdit()
        self.phone_input.setPlaceholderText("+7 (XXX) XXX-XX-XX")
        layout.addWidget(phone_label)
        layout.addWidget(self.phone_input)

        password_label = QLabel("Пароль:")
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        layout.addWidget(password_label)
        layout.addWidget(self.password_input)

        buttons_layout = QHBoxLayout()
        login_btn = QPushButton("Вход")
        login_btn.clicked.connect(self.on_login)
        cancel_btn = QPushButton("Отмена")
        cancel_btn.clicked.connect(self.reject)
        buttons_layout.addWidget(login_btn)
        buttons_layout.addWidget(cancel_btn)
        layout.addLayout(buttons_layout)

        self.setLayout(layout)

    def on_login(self):
        phone = self.phone_input.text().strip()
        password = self.password_input.text().strip()

        if not phone or not password:
            QMessageBox.warning(self, "Ошибка", "Заполните все поля")
            return

        user = authenticate_user(self.db, phone, password)
        if not user:
            QMessageBox.critical(self, "Ошибка", "Неверный номер телефона или пароль")
            return

        if not user.is_active:
            QMessageBox.critical(self, "Ошибка", "Учетная запись заблокирована")
            return

        # Обновляем last_auth_at
        user.last_auth_at = datetime.utcnow()
        self.db.commit()

        self.current_user = user
        self.accept()

    def get_current_user(self):
        return self.current_user
