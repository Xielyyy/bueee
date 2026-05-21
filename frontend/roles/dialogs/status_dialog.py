from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QComboBox,
    QPushButton, QMessageBox
)
from backend.models import RequestStatus

class StatusDialog(QDialog):
    def __init__(self, db, current_status_id=None):
        super().__init__()
        self.db = db
        self.current_status_id = current_status_id
        self.selected_status_id = None
        self.setWindowTitle("Изменить статус")
        self.setGeometry(100, 100, 400, 150)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()

        layout.addWidget(QLabel("Выберите новый статус:"))
        self.status_combo = QComboBox()

        statuses = self.db.query(RequestStatus).all()
        for status in statuses:
            self.status_combo.addItem(status.name, status.id)

        layout.addWidget(self.status_combo)

        buttons = QHBoxLayout()
        ok_btn = QPushButton("OK")
        ok_btn.clicked.connect(self.accept_status)
        cancel_btn = QPushButton("Отмена")
        cancel_btn.clicked.connect(self.reject)
        buttons.addWidget(ok_btn)
        buttons.addWidget(cancel_btn)

        layout.addLayout(buttons)
        self.setLayout(layout)

    def accept_status(self):
        self.selected_status_id = self.status_combo.currentData()
        self.accept()

    def get_selected_status_id(self):
        return self.selected_status_id
