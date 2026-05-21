from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QComboBox,
    QPushButton, QMessageBox
)
from backend.auth import hash_password
from backend.models import User, Role

class UserDialog(QDialog):
    def __init__(self, db):
        super().__init__()
        self.db = db
        self.created_user = None
        self.setWindowTitle("Добавить сотрудника")
        self.setGeometry(100, 100, 500, 400)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()

        layout.addWidget(QLabel("ФИО:"))
        self.full_name = QLineEdit()
        layout.addWidget(self.full_name)

        layout.addWidget(QLabel("Номер телефона:"))
        self.phone = QLineEdit()
        self.phone.setPlaceholderText("+7 (XXX) XXX-XX-XX")
        layout.addWidget(self.phone)

        layout.addWidget(QLabel("Пароль:"))
        self.password = QLineEdit()
        self.password.setEchoMode(QLineEdit.EchoMode.Password)
        layout.addWidget(self.password)

        layout.addWidget(QLabel("Роль:"))
        self.role_combo = QComboBox()
        roles = self.db.query(Role).all()
        for role in roles:
            self.role_combo.addItem(role.name, role.id)
        layout.addWidget(self.role_combo)

        buttons = QHBoxLayout()
        ok_btn = QPushButton("Сохранить")
        ok_btn.clicked.connect(self.save_user)
        cancel_btn = QPushButton("Отмена")
        cancel_btn.clicked.connect(self.reject)
        buttons.addWidget(ok_btn)
        buttons.addWidget(cancel_btn)

        layout.addLayout(buttons)
        self.setLayout(layout)

    def save_user(self):
        full_name = self.full_name.text().strip()
        phone = self.phone.text().strip()
        password = self.password.text().strip()

        if not full_name or not phone or not password:
            QMessageBox.warning(self, "Ошибка", "Заполните все поля")
            return

        existing_user = self.db.query(User).filter(User.phone == phone).first()
        if existing_user:
            QMessageBox.warning(self, "Ошибка", f"Пользователь с номером {phone} уже существует")
            return

        try:
            from backend.models import Master
            user = User(
                full_name=full_name,
                phone=phone,
                password_hash=hash_password(password),
                is_active=True,
                role_id=self.role_combo.currentData()
            )
            self.db.add(user)
            self.db.commit()
            self.db.refresh(user)

            role_id = self.role_combo.currentData()
            role_name = self.role_combo.currentText()
            if role_name == "Мастер по ремонту":
                master = Master(user_id=user.id, is_active=True)
                self.db.add(master)
                self.db.commit()

            self.created_user = user
            QMessageBox.information(self, "Успех", f"Сотрудник '{full_name}' добавлен")
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка при добавлении: {str(e)}")
            self.db.rollback()

    def get_user_data(self):
        return self.created_user
