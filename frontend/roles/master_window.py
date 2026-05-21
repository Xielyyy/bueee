from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTableWidget, QTableWidgetItem,
    QListWidget, QListWidgetItem, QMessageBox, QLabel, QTextEdit
)
from PyQt6.QtCore import Qt
from backend.queries import (
    get_master_requests, get_work_records, update_repair_request_status
)
from backend.models import RequestStatus
from frontend.roles.dialogs.status_dialog import StatusDialog
from frontend.roles.dialogs.work_record_dialog import WorkRecordDialog

class MasterWindow(QWidget):
    def __init__(self, user, db):
        super().__init__()
        self.user = user
        self.db = db
        self.current_master = user.master
        self.current_request_id = None
        self.setup_ui()

    def setup_ui(self):
        main_layout = QVBoxLayout()

        left_layout = QVBoxLayout()
        left_layout.addWidget(QLabel("Назначенные заявки:"))

        self.requests_list = QListWidget()
        self.requests_list.itemClicked.connect(self.on_request_selected)
        left_layout.addWidget(self.requests_list)

        right_layout = QVBoxLayout()
        right_layout.addWidget(QLabel("Детали заявки:"))

        self.details_text = QTextEdit()
        self.details_text.setReadOnly(True)
        right_layout.addWidget(self.details_text)

        right_layout.addWidget(QLabel("История работ:"))
        self.work_records_table = QTableWidget()
        self.work_records_table.setColumnCount(2)
        self.work_records_table.setHorizontalHeaderLabels(["Дата", "Описание"])
        right_layout.addWidget(self.work_records_table)

        buttons_layout = QHBoxLayout()
        add_work_btn = QPushButton("Добавить запись о работе")
        add_work_btn.clicked.connect(self.add_work_record)
        change_status_btn = QPushButton("Изменить статус")
        change_status_btn.clicked.connect(self.change_request_status)
        refresh_btn = QPushButton("Обновить")
        refresh_btn.clicked.connect(self.load_assigned_requests)
        buttons_layout.addWidget(add_work_btn)
        buttons_layout.addWidget(change_status_btn)
        buttons_layout.addWidget(refresh_btn)
        right_layout.addLayout(buttons_layout)

        content_layout = QHBoxLayout()
        content_layout.addLayout(left_layout, 1)
        content_layout.addLayout(right_layout, 2)

        main_layout.addLayout(content_layout)
        self.setLayout(main_layout)

        self.load_assigned_requests()

    def load_assigned_requests(self):
        self.requests_list.clear()
        requests = get_master_requests(self.db, self.current_master.id)
        for req in requests:
            status_color = ""
            if req.status.name == "На выполнении":
                status_color = " ⏳"
            elif req.status.name == "Выполнена":
                status_color = " ✓"
            item = QListWidgetItem(f"#{req.id} - {req.client.full_name}{status_color}")
            item.setData(Qt.ItemDataRole.UserRole, req.id)
            self.requests_list.addItem(item)

    def on_request_selected(self, item):
        request_id = item.data(Qt.ItemDataRole.UserRole)
        self.current_request_id = request_id
        from backend.queries import get_repair_request
        request = get_repair_request(self.db, request_id)
        if request:
            self.details_text.setText(
                f"ID заявки: {request.id}\n"
                f"Клиент: {request.client.full_name}\n"
                f"Телефон: {request.client.phone}\n"
                f"Устройство: {request.device.device_type} - {request.device.model_name}\n"
                f"Серийный номер: {request.device.serial_number}\n"
                f"Проблема: {request.problem_description}\n"
                f"Статус: {request.status.name}\n"
                f"Приоритет: {request.priority.name}\n"
                f"Тип ремонта: {request.repair_type.name}\n"
                f"Дата создания: {request.created_at.strftime('%Y-%m-%d %H:%M')}"
            )
            self.load_work_records(request_id)

    def load_work_records(self, request_id):
        self.work_records_table.setRowCount(0)
        records = get_work_records(self.db, request_id)
        for record in records:
            row = self.work_records_table.rowCount()
            self.work_records_table.insertRow(row)
            self.work_records_table.setItem(row, 0, QTableWidgetItem(record.created_at.strftime("%Y-%m-%d %H:%M")))

            consumables_info = ""
            if record.consumables:
                consumables_info = " [" + ", ".join([f"{c.consumable.name}x{c.quantity_used}" for c in record.consumables]) + "]"

            self.work_records_table.setItem(row, 1, QTableWidgetItem(record.work_description + consumables_info))

    def add_work_record(self):
        if not self.current_request_id:
            QMessageBox.warning(self, "Ошибка", "Выберите заявку")
            return

        try:
            dialog = WorkRecordDialog(self.db, self.current_master.id, self.current_request_id)
            if dialog.exec() == dialog.DialogCode.Accepted:
                self.load_work_records(self.current_request_id)
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка при добавлении записи: {str(e)}")
            print(f"Error: {e}")

    def change_request_status(self):
        if not self.current_request_id:
            QMessageBox.warning(self, "Ошибка", "Выберите заявку")
            return

        try:
            dialog = StatusDialog(self.db)
            if dialog.exec() == dialog.DialogCode.Accepted:
                new_status_id = dialog.get_selected_status_id()
                if new_status_id:
                    update_repair_request_status(self.db, self.current_request_id, new_status_id)
                    QMessageBox.information(self, "Успех", "Статус заявки изменен")
                    self.load_assigned_requests()
                    if self.requests_list.count() > 0:
                        self.requests_list.setCurrentRow(0)
                        self.on_request_selected(self.requests_list.item(0))
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка при изменении статуса: {str(e)}")
            print(f"Error: {e}")
