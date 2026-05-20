from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QTextEdit,
    QPushButton, QMessageBox
)
from backend.queries import (
    search_clients, get_client_devices, create_device,
    create_repair_request
)
from backend.models import RequestStatus, RequestPriority, RepairType

class RequestDialog(QDialog):
    def __init__(self, user, db):
        super().__init__()
        self.user = user
        self.db = db
        self.setWindowTitle("Создать новую заявку")
        self.setGeometry(100, 100, 600, 500)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()

        # Выбор клиента
        layout.addWidget(QLabel("Клиент:"))
        self.client_combo = QComboBox()
        self.client_combo.currentIndexChanged.connect(self.on_client_changed)
        layout.addWidget(self.client_combo)

        # Выбор или регистрация устройства
        layout.addWidget(QLabel("Устройство:"))
        device_layout = QHBoxLayout()
        self.device_combo = QComboBox()
        device_layout.addWidget(self.device_combo)
        add_device_btn = QPushButton("Добавить новое")
        add_device_btn.clicked.connect(self.add_new_device)
        device_layout.addWidget(add_device_btn)
        layout.addLayout(device_layout)

        # Описание проблемы
        layout.addWidget(QLabel("Описание проблемы:"))
        self.problem_text = QTextEdit()
        layout.addWidget(self.problem_text)

        # Тип ремонта
        layout.addWidget(QLabel("Тип ремонта:"))
        self.repair_type_combo = QComboBox()
        layout.addWidget(self.repair_type_combo)

        # Приоритет
        layout.addWidget(QLabel("Приоритет:"))
        self.priority_combo = QComboBox()
        layout.addWidget(self.priority_combo)

        # Мастера
        layout.addWidget(QLabel("Назначить мастеров:"))
        self.masters_list = QComboBox()
        layout.addWidget(self.masters_list)

        buttons = QHBoxLayout()
        ok_btn = QPushButton("Создать заявку")
        ok_btn.clicked.connect(self.create_request)
        cancel_btn = QPushButton("Отмена")
        cancel_btn.clicked.connect(self.reject)
        buttons.addWidget(ok_btn)
        buttons.addWidget(cancel_btn)
        layout.addLayout(buttons)

        self.setLayout(layout)
        self.load_data()

    def load_data(self):
        # Загружаем клиентов
        from backend.models import Client
        clients = self.db.query(Client).all()
        for client in clients:
            self.client_combo.addItem(client.full_name, client.id)

        # Загружаем типы ремонта
        repair_types = self.db.query(RepairType).all()
        for rt in repair_types:
            self.repair_type_combo.addItem(rt.name, rt.id)

        # Загружаем приоритеты
        priorities = self.db.query(RequestPriority).all()
        for p in priorities:
            self.priority_combo.addItem(p.name, p.id)

        # Загружаем мастеров
        from backend.models import Master
        masters = self.db.query(Master).filter(Master.is_active == True).all()
        for m in masters:
            self.masters_list.addItem(m.user.full_name, m.id)

    def on_client_changed(self):
        self.device_combo.clear()
        client_id = self.client_combo.currentData()
        if client_id:
            devices = get_client_devices(self.db, client_id)
            for device in devices:
                self.device_combo.addItem(f"{device.device_type} - {device.model_name}", device.id)

    def add_new_device(self):
        from frontend.roles.dialogs.device_dialog import DeviceDialog
        client_id = self.client_combo.currentData()
        if not client_id:
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.warning(self, "Ошибка", "Сначала выберите клиента")
            return

        device_dialog = DeviceDialog(self.db)
        device_dialog.set_client_id(client_id)
        if device_dialog.exec() == device_dialog.DialogCode.Accepted:
            device = device_dialog.get_device_data()
            if device:
                self.device_combo.addItem(f"{device.device_type} - {device.model_name}", device.id)
                self.device_combo.setCurrentIndex(self.device_combo.count() - 1)

    def create_request(self):
        if not self.problem_text.toPlainText().strip():
            QMessageBox.warning(self, "Ошибка", "Заполните описание проблемы")
            return

        client_id = self.client_combo.currentData()
        device_id = self.device_combo.currentData()
        repair_type_id = self.repair_type_combo.currentData()
        priority_id = self.priority_combo.currentData()

        # Получаем статус "Новая"
        new_status = self.db.query(RequestStatus).filter(RequestStatus.name == "Новая").first()

        request = create_repair_request(
            self.db,
            problem_description=self.problem_text.toPlainText(),
            client_id=client_id,
            device_id=device_id,
            created_by_user_id=self.user.id,
            status_id=new_status.id,
            priority_id=priority_id,
            repair_type_id=repair_type_id
        )

        # Назначаем мастера
        if self.masters_list.currentData():
            from backend.models import RequestMaster
            assignment = RequestMaster(
                repair_request_id=request.id,
                master_id=self.masters_list.currentData()
            )
            self.db.add(assignment)
            self.db.commit()

        QMessageBox.information(self, "Успех", f"Заявка #{request.id} создана")
        self.accept()
