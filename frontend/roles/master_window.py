from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTableWidget, QTableWidgetItem,
    QListWidget, QListWidgetItem, QMessageBox, QSpinBox, QComboBox, QLabel, QTextEdit
)
from PyQt6.QtCore import Qt
from backend.queries import (
    get_master_requests, get_work_records, create_work_record,
    get_all_consumables, deduct_consumable, get_all_requests
)
from backend.models import RequestStatus

class MasterWindow(QWidget):
    def __init__(self, user, db):
        super().__init__()
        self.user = user
        self.db = db
        self.current_master = user.master
        self.setup_ui()

    def setup_ui(self):
        main_layout = QVBoxLayout()

        # Левая часть: список заявок
        left_layout = QVBoxLayout()
        left_layout.addWidget(QLabel("Назначенные заявки:"))

        self.requests_list = QListWidget()
        self.requests_list.itemClicked.connect(self.on_request_selected)
        left_layout.addWidget(self.requests_list)

        # Правая часть: детали заявки
        right_layout = QVBoxLayout()
        right_layout.addWidget(QLabel("Детали заявки:"))

        self.details_text = QTextEdit()
        self.details_text.setReadOnly(True)
        right_layout.addWidget(self.details_text)

        # Таблица работ
        right_layout.addWidget(QLabel("История работ:"))
        self.work_records_table = QTableWidget()
        self.work_records_table.setColumnCount(3)
        self.work_records_table.setHorizontalHeaderLabels(["Дата", "Описание", ""])
        right_layout.addWidget(self.work_records_table)

        # Управление запчастями
        consumables_layout = QVBoxLayout()
        consumables_layout.addWidget(QLabel("Запчасти:"))

        self.consumables_combo = QComboBox()
        consumables_layout.addWidget(self.consumables_combo)

        qty_layout = QHBoxLayout()
        qty_layout.addWidget(QLabel("Количество:"))
        self.consumable_qty = QSpinBox()
        self.consumable_qty.setMinimum(1)
        qty_layout.addWidget(self.consumable_qty)
        consumables_layout.addLayout(qty_layout)

        add_consumable_btn = QPushButton("Добавить запчасть")
        add_consumable_btn.clicked.connect(self.add_consumable)
        consumables_layout.addWidget(add_consumable_btn)
        right_layout.addLayout(consumables_layout)

        # Кнопки управления статусом
        status_layout = QHBoxLayout()
        change_status_btn = QPushButton("Изменить статус")
        change_status_btn.clicked.connect(self.change_request_status)
        status_layout.addWidget(change_status_btn)
        right_layout.addLayout(status_layout)

        # Общий layout
        content_layout = QHBoxLayout()
        content_layout.addLayout(left_layout, 1)
        content_layout.addLayout(right_layout, 2)

        main_layout.addLayout(content_layout)
        self.setLayout(main_layout)

        self.load_assigned_requests()
        self.load_consumables()

    def load_assigned_requests(self):
        self.requests_list.clear()
        requests = get_master_requests(self.db, self.current_master.id)
        for req in requests:
            item = QListWidgetItem(f"#{req.id} - {req.client.full_name}")
            item.setData(Qt.ItemDataRole.UserRole, req.id)
            self.requests_list.addItem(item)

    def on_request_selected(self, item):
        request_id = item.data(Qt.ItemDataRole.UserRole)
        # Загрузить детали заявки
        from backend.queries import get_repair_request
        request = get_repair_request(self.db, request_id)
        if request:
            self.details_text.setText(
                f"Клиент: {request.client.full_name}\n"
                f"Устройство: {request.device.model_name}\n"
                f"Проблема: {request.problem_description}\n"
                f"Статус: {request.status.name}"
            )
            self.load_work_records(request_id)

    def load_work_records(self, request_id):
        self.work_records_table.setRowCount(0)
        records = get_work_records(self.db, request_id)
        for record in records:
            row = self.work_records_table.rowCount()
            self.work_records_table.insertRow(row)
            self.work_records_table.setItem(row, 0, QTableWidgetItem(record.created_at.strftime("%Y-%m-%d %H:%M")))
            self.work_records_table.setItem(row, 1, QTableWidgetItem(record.work_description))

    def load_consumables(self):
        self.consumables_combo.clear()
        consumables = get_all_consumables(self.db)
        for c in consumables:
            self.consumables_combo.addItem(f"{c.name} ({c.quantity} шт)", c.id)

    def change_request_status(self):
        current_item = self.requests_list.currentItem()
        if not current_item:
            QMessageBox.warning(self, "Ошибка", "Выберите заявку")
            return

        request_id = current_item.data(Qt.ItemDataRole.UserRole)
        # TODO: Диалог выбора статуса
        QMessageBox.information(self, "Информация", "Функция в разработке")

    def add_consumable(self):
        if not self.requests_list.currentItem():
            QMessageBox.warning(self, "Ошибка", "Выберите заявку")
            return
        QMessageBox.information(self, "Информация", "Функция добавления запчасти в разработке")
