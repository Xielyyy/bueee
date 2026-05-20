from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTabWidget,
    QTableWidget, QTableWidgetItem, QMessageBox, QDateEdit, QLabel
)
from PyQt6.QtCore import Qt, QDate
from datetime import datetime
from backend.queries import get_all_requests, search_clients, create_client
from backend.queries import create_device, create_repair_request, get_active_masters
from backend.models import RequestStatus, RequestPriority, RepairType
from frontend.roles.dialogs.client_dialog import ClientDialog
from frontend.roles.dialogs.request_dialog import RequestDialog

class OperatorWindow(QWidget):
    def __init__(self, user, db):
        super().__init__()
        self.user = user
        self.db = db
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()

        tabs = QTabWidget()

        # Вкладка: Управление клиентами
        client_tab = QWidget()
        client_layout = QVBoxLayout()
        self.client_btn = QPushButton("Добавить нового клиента")
        self.client_btn.clicked.connect(self.add_new_client)
        client_layout.addWidget(self.client_btn)
        client_tab.setLayout(client_layout)
        tabs.addTab(client_tab, "Клиенты")

        # Вкладка: Управление заявками
        request_tab = QWidget()
        request_layout = QVBoxLayout()

        filter_layout = QHBoxLayout()
        filter_layout.addWidget(QLabel("Дата начала:"))
        self.start_date = QDateEdit()
        self.start_date.setDate(QDate.currentDate().addMonths(-1))
        filter_layout.addWidget(self.start_date)

        filter_layout.addWidget(QLabel("Дата конца:"))
        self.end_date = QDateEdit()
        self.end_date.setDate(QDate.currentDate())
        filter_layout.addWidget(self.end_date)

        filter_btn = QPushButton("Показать")
        filter_btn.clicked.connect(self.filter_requests)
        filter_layout.addWidget(filter_btn)

        show_all_btn = QPushButton("Показать все")
        show_all_btn.clicked.connect(self.show_all_requests)
        filter_layout.addWidget(show_all_btn)

        request_layout.addLayout(filter_layout)

        self.requests_table = QTableWidget()
        self.requests_table.setColumnCount(6)
        self.requests_table.setHorizontalHeaderLabels(
            ["ID", "Клиент", "Устройство", "Статус", "Приоритет", "Дата создания"]
        )
        request_layout.addWidget(self.requests_table)

        new_request_btn = QPushButton("Создать новую заявку")
        new_request_btn.clicked.connect(self.create_new_request)
        request_layout.addWidget(new_request_btn)

        request_tab.setLayout(request_layout)
        tabs.addTab(request_tab, "Заявки")

        layout.addWidget(tabs)
        self.setLayout(layout)
        self.load_all_requests()

    def add_new_client(self):
        try:
            dialog = ClientDialog(self.db)
            if dialog.exec() == dialog.DialogCode.Accepted:
                client = dialog.get_client_data()
                if client:
                    QMessageBox.information(self, "Успех", f"Клиент '{client.full_name}' добавлен")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка при добавлении клиента: {str(e)}")
            print(f"Error: {e}")

    def create_new_request(self):
        try:
            dialog = RequestDialog(self.user, self.db)
            if dialog.exec() == dialog.DialogCode.Accepted:
                QMessageBox.information(self, "Успех", "Заявка успешно создана")
                self.load_all_requests()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка при создании заявки: {str(e)}")
            print(f"Error: {e}")

    def load_all_requests(self):
        requests = get_all_requests(self.db)
        self.populate_requests_table(requests)

    def filter_requests(self):
        start = datetime.combine(self.start_date.date().toPyDate(), datetime.min.time())
        end = datetime.combine(self.end_date.date().toPyDate(), datetime.max.time())
        requests = get_all_requests(self.db, start, end)
        self.populate_requests_table(requests)

    def show_all_requests(self):
        self.load_all_requests()

    def populate_requests_table(self, requests):
        self.requests_table.setRowCount(0)
        for request in requests:
            row = self.requests_table.rowCount()
            self.requests_table.insertRow(row)
            self.requests_table.setItem(row, 0, QTableWidgetItem(str(request.id)))
            self.requests_table.setItem(row, 1, QTableWidgetItem(request.client.full_name))
            self.requests_table.setItem(row, 2, QTableWidgetItem(request.device.model_name))
            self.requests_table.setItem(row, 3, QTableWidgetItem(request.status.name))
            self.requests_table.setItem(row, 4, QTableWidgetItem(request.priority.name))
            self.requests_table.setItem(row, 5, QTableWidgetItem(request.created_at.strftime("%Y-%m-%d %H:%M")))
