from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTabWidget,
    QTableWidget, QTableWidgetItem, QMessageBox, QDateEdit, QLabel,
    QLineEdit, QDoubleSpinBox
)
from PyQt6.QtCore import Qt, QDate
from datetime import datetime
from backend.queries import get_all_requests, search_clients, create_client
from backend.queries import create_device, create_repair_request, get_active_masters
from backend.models import RequestStatus, RequestPriority, RepairType, Client
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

        client_search_layout = QHBoxLayout()
        client_search_layout.addWidget(QLabel("Поиск клиента:"))
        self.client_search = QLineEdit()
        self.client_search.setPlaceholderText("Введите имя или телефон")
        client_search_layout.addWidget(self.client_search)
        search_client_btn = QPushButton("Найти")
        search_client_btn.clicked.connect(self.search_clients_by_name)
        client_search_layout.addWidget(search_client_btn)
        client_layout.addLayout(client_search_layout)

        self.clients_table = QTableWidget()
        self.clients_table.setColumnCount(5)
        self.clients_table.setHorizontalHeaderLabels(["ФИО", "Телефон", "Дата рождения", "Паспорт", "Адреса"])
        self.clients_table.setColumnWidth(0, 200)
        self.clients_table.setColumnWidth(1, 150)
        self.clients_table.setColumnWidth(2, 130)
        client_layout.addWidget(self.clients_table)

        client_buttons_layout = QHBoxLayout()
        add_client_btn = QPushButton("Добавить нового клиента")
        add_client_btn.clicked.connect(self.add_new_client)
        load_all_clients_btn = QPushButton("Показать всех")
        load_all_clients_btn.clicked.connect(self.load_all_clients)
        client_buttons_layout.addWidget(add_client_btn)
        client_buttons_layout.addWidget(load_all_clients_btn)
        client_layout.addLayout(client_buttons_layout)

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

        filter_btn = QPushButton("Фильтровать")
        filter_btn.clicked.connect(self.filter_requests)
        filter_layout.addWidget(filter_btn)

        show_all_btn = QPushButton("Все заявки")
        show_all_btn.clicked.connect(self.show_all_requests)
        filter_layout.addWidget(show_all_btn)

        request_layout.addLayout(filter_layout)

        self.requests_table = QTableWidget()
        self.requests_table.setColumnCount(6)
        self.requests_table.setHorizontalHeaderLabels(
            ["ID", "Клиент", "Устройство", "Статус", "Приоритет", "Дата создания"]
        )
        self.requests_table.setColumnWidth(0, 50)
        self.requests_table.setColumnWidth(1, 150)
        self.requests_table.setColumnWidth(2, 150)
        self.requests_table.setColumnWidth(3, 120)
        self.requests_table.setColumnWidth(4, 100)
        self.requests_table.setColumnWidth(5, 150)
        self.requests_table.itemClicked.connect(self.on_request_selected)
        request_layout.addWidget(self.requests_table)

        request_buttons_layout = QHBoxLayout()
        new_request_btn = QPushButton("Создать новую заявку")
        new_request_btn.clicked.connect(self.create_new_request)
        view_request_btn = QPushButton("Просмотреть детали")
        view_request_btn.clicked.connect(self.view_request_details)
        mark_paid_btn = QPushButton("Отметить как оплачено")
        mark_paid_btn.clicked.connect(self.mark_request_paid)
        request_buttons_layout.addWidget(new_request_btn)
        request_buttons_layout.addWidget(view_request_btn)
        request_buttons_layout.addWidget(mark_paid_btn)
        request_layout.addLayout(request_buttons_layout)

        request_tab.setLayout(request_layout)
        tabs.addTab(request_tab, "Заявки")

        layout.addWidget(tabs)
        self.setLayout(layout)
        self.load_all_requests()
        self.load_all_clients()

    def load_all_clients(self):
        try:
            clients = self.db.query(Client).all()
            self.populate_clients_table(clients)
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка при загрузке клиентов: {str(e)}")

    def search_clients_by_name(self):
        search_text = self.client_search.text().strip()
        if not search_text:
            self.load_all_clients()
            return

        try:
            clients = search_clients(self.db, full_name=search_text) or search_clients(self.db, phone=search_text)
            self.populate_clients_table(clients if clients else [])
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка при поиске: {str(e)}")

    def populate_clients_table(self, clients):
        self.clients_table.setRowCount(0)
        for client in clients:
            row = self.clients_table.rowCount()
            self.clients_table.insertRow(row)
            self.clients_table.setItem(row, 0, QTableWidgetItem(client.full_name))
            self.clients_table.setItem(row, 1, QTableWidgetItem(client.phone))
            birth_date = client.birth_date.strftime("%Y-%m-%d") if client.birth_date else ""
            self.clients_table.setItem(row, 2, QTableWidgetItem(birth_date))
            passport = f"{client.passport_series} {client.passport_number}" if client.passport_series else "-"
            self.clients_table.setItem(row, 3, QTableWidgetItem(passport))
            devices_count = len(client.devices) if client.devices else 0
            self.clients_table.setItem(row, 4, QTableWidgetItem(f"{devices_count} устройств"))

    def add_new_client(self):
        try:
            dialog = ClientDialog(self.db)
            if dialog.exec() == dialog.DialogCode.Accepted:
                client = dialog.get_client_data()
                if client:
                    QMessageBox.information(self, "Успех", f"Клиент '{client.full_name}' добавлен")
                    self.load_all_clients()
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

    def on_request_selected(self, item):
        pass

    def view_request_details(self):
        if self.requests_table.currentRow() < 0:
            QMessageBox.warning(self, "Ошибка", "Выберите заявку")
            return

        request_id = int(self.requests_table.item(self.requests_table.currentRow(), 0).text())
        from backend.queries import get_repair_request
        request = get_repair_request(self.db, request_id)

        if request:
            details = (
                f"ID: {request.id}\n"
                f"Клиент: {request.client.full_name}\n"
                f"Телефон: {request.client.phone}\n"
                f"Устройство: {request.device.device_type} - {request.device.model_name}\n"
                f"Серийный номер: {request.device.serial_number}\n"
                f"Проблема: {request.problem_description}\n"
                f"Статус: {request.status.name}\n"
                f"Приоритет: {request.priority.name}\n"
                f"Тип ремонта: {request.repair_type.name}\n"
                f"Дата создания: {request.created_at.strftime('%Y-%m-%d %H:%M')}\n"
                f"Оплачено: {'Да' if request.is_paid else 'Нет'}"
            )
            QMessageBox.information(self, f"Заявка #{request_id}", details)

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

    def mark_request_paid(self):
        if self.requests_table.currentRow() < 0:
            QMessageBox.warning(self, "Ошибка", "Выберите заявку")
            return

        try:
            request_id = int(self.requests_table.item(self.requests_table.currentRow(), 0).text())
            from backend.queries import get_repair_request
            request = get_repair_request(self.db, request_id)

            if request:
                if request.is_paid:
                    QMessageBox.information(self, "Информация", "Заявка уже отмечена как оплаченная")
                    return

                request.is_paid = True
                self.db.commit()
                QMessageBox.information(self, "Успех", "Заявка отмечена как оплаченная")
                self.load_all_requests()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка при отметке оплаты: {str(e)}")
            print(f"Error: {e}")
