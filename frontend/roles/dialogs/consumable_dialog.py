from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QDoubleSpinBox,
    QPushButton, QMessageBox, QSpinBox, QComboBox
)
from backend.models import Consumable


class ConsumableDialog(QDialog):
    def __init__(self, db):
        super().__init__()
        self.db = db
        self.created_consumable = None
        self.setWindowTitle("Добавить расходник")
        self.setGeometry(100, 100, 500, 400)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()

        layout.addWidget(QLabel("Название:"))
        self.name = QLineEdit()
        layout.addWidget(self.name)

        layout.addWidget(QLabel("Производитель:"))
        self.manufacturer = QLineEdit()
        layout.addWidget(self.manufacturer)

        layout.addWidget(QLabel("Тип устройства:"))
        self.device_type = QComboBox()
        self.device_type.addItems(["Ноутбук", "Смартфон", "Планшет", "Монитор", "Принтер", "Другое"])
        layout.addWidget(self.device_type)

        layout.addWidget(QLabel("Цена (руб.):"))
        self.price = QDoubleSpinBox()
        self.price.setMinimum(0)
        self.price.setMaximum(999999)
        self.price.setDecimals(2)
        layout.addWidget(self.price)

        layout.addWidget(QLabel("Остаток на складе:"))
        self.quantity = QSpinBox()
        self.quantity.setMinimum(0)
        self.quantity.setMaximum(10000)
        layout.addWidget(self.quantity)

        buttons = QHBoxLayout()
        ok_btn = QPushButton("Сохранить")
        ok_btn.clicked.connect(self.save_consumable)
        cancel_btn = QPushButton("Отмена")
        cancel_btn.clicked.connect(self.reject)
        buttons.addWidget(ok_btn)
        buttons.addWidget(cancel_btn)

        layout.addLayout(buttons)
        self.setLayout(layout)

    def save_consumable(self):
        name = self.name.text().strip()
        if not name:
            QMessageBox.warning(self, "Ошибка", "Заполните название")
            return

        existing = self.db.query(Consumable).filter(Consumable.name == name).first()
        if existing:
            QMessageBox.warning(self, "Ошибка", f"Расходник '{name}' уже существует")
            return

        try:
            consumable = Consumable(
                name=name,
                manufacturer=self.manufacturer.text() or None,
                device_type=self.device_type.currentText(),
                price=self.price.value(),
                quantity=self.quantity.value()
            )
            self.db.add(consumable)
            self.db.commit()
            self.db.refresh(consumable)
            self.created_consumable = consumable
            QMessageBox.information(self, "Успех", f"Расходник '{name}' добавлен")
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка при добавлении: {str(e)}")
            self.db.rollback()

    def get_consumable_data(self):
        return self.created_consumable
