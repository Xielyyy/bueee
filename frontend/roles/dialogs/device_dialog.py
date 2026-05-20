from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QMessageBox, QComboBox
)
from backend.queries import create_device

class DeviceDialog(QDialog):
    def __init__(self, db):
        super().__init__()
        self.db = db
        self.created_device = None
        self.setWindowTitle("Добавить устройство")
        self.setGeometry(100, 100, 500, 300)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()

        layout.addWidget(QLabel("Тип устройства:"))
        self.device_type = QComboBox()
        self.device_type.addItems(["Ноутбук", "Смартфон", "Планшет", "Монитор", "Принтер", "Другое"])
        layout.addWidget(self.device_type)

        layout.addWidget(QLabel("Марка/Модель:"))
        self.model_name = QLineEdit()
        layout.addWidget(self.model_name)

        layout.addWidget(QLabel("Серийный номер:"))
        self.serial_number = QLineEdit()
        layout.addWidget(self.serial_number)

        # Hidden: client_id будет установлен при создании из контекста
        self.client_id = None

        buttons = QHBoxLayout()
        ok_btn = QPushButton("Добавить")
        ok_btn.clicked.connect(self.save_device)
        cancel_btn = QPushButton("Отмена")
        cancel_btn.clicked.connect(self.reject)
        buttons.addWidget(ok_btn)
        buttons.addWidget(cancel_btn)

        layout.addLayout(buttons)
        self.setLayout(layout)

    def set_client_id(self, client_id):
        self.client_id = client_id

    def save_device(self):
        if not self.model_name.text() or not self.serial_number.text():
            QMessageBox.warning(self, "Ошибка", "Заполните все поля")
            return

        if not self.client_id:
            QMessageBox.warning(self, "Ошибка", "Клиент не выбран")
            return

        self.created_device = create_device(
            self.db,
            device_type=self.device_type.currentText(),
            model_name=self.model_name.text(),
            serial_number=self.serial_number.text(),
            client_id=self.client_id
        )
        self.accept()

    def get_device_data(self):
        return self.created_device
