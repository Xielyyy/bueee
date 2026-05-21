from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QSpinBox,
    QPushButton, QMessageBox, QDoubleSpinBox
)
from backend.models import Service

class ServiceDialog(QDialog):
    def __init__(self, db):
        super().__init__()
        self.db = db
        self.created_service = None
        self.setWindowTitle("Добавить услугу")
        self.setGeometry(100, 100, 500, 300)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()

        layout.addWidget(QLabel("Название услуги:"))
        self.name = QLineEdit()
        layout.addWidget(self.name)

        layout.addWidget(QLabel("Цена (руб.):"))
        self.price = QDoubleSpinBox()
        self.price.setMinimum(0)
        self.price.setMaximum(999999)
        self.price.setDecimals(2)
        layout.addWidget(self.price)

        layout.addWidget(QLabel("Продолжительность (минут):"))
        self.duration = QSpinBox()
        self.duration.setMinimum(1)
        self.duration.setMaximum(999)
        layout.addWidget(self.duration)

        buttons = QHBoxLayout()
        ok_btn = QPushButton("Сохранить")
        ok_btn.clicked.connect(self.save_service)
        cancel_btn = QPushButton("Отмена")
        cancel_btn.clicked.connect(self.reject)
        buttons.addWidget(ok_btn)
        buttons.addWidget(cancel_btn)

        layout.addLayout(buttons)
        self.setLayout(layout)

    def save_service(self):
        name = self.name.text().strip()
        if not name:
            QMessageBox.warning(self, "Ошибка", "Заполните название услуги")
            return

        existing = self.db.query(Service).filter(Service.name == name).first()
        if existing:
            QMessageBox.warning(self, "Ошибка", f"Услуга '{name}' уже существует")
            return

        try:
            service = Service(
                name=name,
                price=self.price.value(),
                duration_minutes=self.duration.value(),
                is_available=True
            )
            self.db.add(service)
            self.db.commit()
            self.db.refresh(service)
            self.created_service = service
            QMessageBox.information(self, "Успех", f"Услуга '{name}' добавлена")
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка при добавлении: {str(e)}")
            self.db.rollback()

    def get_service_data(self):
        return self.created_service
