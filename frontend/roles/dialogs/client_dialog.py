from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QDateEdit,
    QPushButton, QMessageBox
)
from PyQt6.QtCore import QDate
from backend.queries import create_client
from datetime import date

class ClientDialog(QDialog):
    def __init__(self, db):
        super().__init__()
        self.db = db
        self.created_client = None
        self.setWindowTitle("Добавить клиента")
        self.setGeometry(100, 100, 500, 400)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()

        layout.addWidget(QLabel("ФИО:"))
        self.full_name = QLineEdit()
        layout.addWidget(self.full_name)

        layout.addWidget(QLabel("Номер телефона:"))
        self.phone = QLineEdit()
        layout.addWidget(self.phone)

        layout.addWidget(QLabel("Дата рождения:"))
        self.birth_date = QDateEdit()
        self.birth_date.setDate(QDate.currentDate())
        layout.addWidget(self.birth_date)

        layout.addWidget(QLabel("Серия паспорта:"))
        self.passport_series = QLineEdit()
        layout.addWidget(self.passport_series)

        layout.addWidget(QLabel("Номер паспорта:"))
        self.passport_number = QLineEdit()
        layout.addWidget(self.passport_number)

        layout.addWidget(QLabel("Выдан кем:"))
        self.passport_issued_by = QLineEdit()
        layout.addWidget(self.passport_issued_by)

        layout.addWidget(QLabel("Дата выдачи:"))
        self.passport_issue_date = QDateEdit()
        self.passport_issue_date.setDate(QDate.currentDate())
        layout.addWidget(self.passport_issue_date)

        buttons = QHBoxLayout()
        ok_btn = QPushButton("Сохранить")
        ok_btn.clicked.connect(self.save_client)
        cancel_btn = QPushButton("Отмена")
        cancel_btn.clicked.connect(self.reject)
        buttons.addWidget(ok_btn)
        buttons.addWidget(cancel_btn)

        layout.addLayout(buttons)
        self.setLayout(layout)

    def save_client(self):
        if not self.full_name.text() or not self.phone.text():
            QMessageBox.warning(self, "Ошибка", "Заполните ФИО и телефон")
            return

        self.created_client = create_client(
            self.db,
            full_name=self.full_name.text(),
            phone=self.phone.text(),
            birth_date=self.birth_date.date().toPyDate(),
            passport_series=self.passport_series.text(),
            passport_number=self.passport_number.text(),
            passport_issued_by=self.passport_issued_by.text(),
            passport_issue_date=self.passport_issue_date.date().toPyDate()
        )
        self.accept()

    def get_client_data(self):
        return self.created_client
