from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTabWidget, QTableWidget,
    QTableWidgetItem, QMessageBox, QLabel
)
from PyQt6.QtCore import Qt
from backend.queries import (
    get_unpaid_completed_requests, get_low_stock_consumables,
    get_idle_masters, calculate_repair_cost
)
from backend.models import User, Service, Master, Consumable
from frontend.roles.dialogs.user_dialog import UserDialog
from frontend.roles.dialogs.service_dialog import ServiceDialog

class AdminWindow(QWidget):
    def __init__(self, user, db):
        super().__init__()
        self.user = user
        self.db = db
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()

        tabs = QTabWidget()

        # Вкладка: Администрирование персонала
        staff_tab = QWidget()
        staff_layout = QVBoxLayout()
        add_staff_btn = QPushButton("Добавить сотрудника")
        add_staff_btn.clicked.connect(self.add_staff)
        staff_layout.addWidget(add_staff_btn)

        self.staff_table = QTableWidget()
        self.staff_table.setColumnCount(4)
        self.staff_table.setHorizontalHeaderLabels(["ФИО", "Роль", "Телефон", "Активен"])
        self.staff_table.setColumnWidth(0, 200)
        self.staff_table.setColumnWidth(1, 200)
        self.staff_table.setColumnWidth(2, 150)
        self.staff_table.setColumnWidth(3, 80)
        staff_layout.addWidget(self.staff_table)

        refresh_staff_btn = QPushButton("Обновить список")
        refresh_staff_btn.clicked.connect(self.load_staff)
        staff_layout.addWidget(refresh_staff_btn)

        staff_tab.setLayout(staff_layout)
        tabs.addTab(staff_tab, "Персонал")

        # Вкладка: Справочники
        reference_tab = QWidget()
        reference_layout = QVBoxLayout()

        reference_layout.addWidget(QLabel("Управление услугами:"))
        self.services_table = QTableWidget()
        self.services_table.setColumnCount(3)
        self.services_table.setHorizontalHeaderLabels(["Название", "Цена (руб.)", "Длительность (мин)"])
        self.services_table.setColumnWidth(0, 250)
        self.services_table.setColumnWidth(1, 150)
        self.services_table.setColumnWidth(2, 150)
        reference_layout.addWidget(self.services_table)

        add_service_btn = QPushButton("Добавить услугу")
        add_service_btn.clicked.connect(self.add_service)
        refresh_services_btn = QPushButton("Обновить список")
        refresh_services_btn.clicked.connect(self.load_services)

        services_buttons = QHBoxLayout()
        services_buttons.addWidget(add_service_btn)
        services_buttons.addWidget(refresh_services_btn)
        reference_layout.addLayout(services_buttons)

        reference_layout.addWidget(QLabel("Управление расходниками:"))
        self.consumables_table = QTableWidget()
        self.consumables_table.setColumnCount(5)
        self.consumables_table.setHorizontalHeaderLabels(["Название", "Производитель", "Цена (руб.)", "Остаток", "Тип устройства"])
        self.consumables_table.setColumnWidth(0, 150)
        self.consumables_table.setColumnWidth(1, 150)
        self.consumables_table.setColumnWidth(2, 120)
        self.consumables_table.setColumnWidth(3, 80)
        self.consumables_table.setColumnWidth(4, 120)
        reference_layout.addWidget(self.consumables_table)

        add_consumable_btn = QPushButton("Добавить расходник")
        add_consumable_btn.clicked.connect(self.add_consumable)
        refresh_consumables_btn = QPushButton("Обновить список")
        refresh_consumables_btn.clicked.connect(self.load_consumables)

        consumables_buttons = QHBoxLayout()
        consumables_buttons.addWidget(add_consumable_btn)
        consumables_buttons.addWidget(refresh_consumables_btn)
        reference_layout.addLayout(consumables_buttons)

        reference_tab.setLayout(reference_layout)
        tabs.addTab(reference_tab, "Справочники")

        # Вкладка: Отчеты
        reports_tab = QWidget()
        reports_layout = QVBoxLayout()

        reports_layout.addWidget(QLabel("Должники:"))
        self.debtors_table = QTableWidget()
        self.debtors_table.setColumnCount(4)
        self.debtors_table.setHorizontalHeaderLabels(["ID заявки", "Клиент", "Сумма (руб.)", "Дата"])
        reports_layout.addWidget(self.debtors_table)

        load_debtors_btn = QPushButton("Загрузить должников")
        load_debtors_btn.clicked.connect(self.load_debtors)
        reports_layout.addWidget(load_debtors_btn)

        reports_layout.addWidget(QLabel("Дефицит склада:"))
        self.low_stock_table = QTableWidget()
        self.low_stock_table.setColumnCount(4)
        self.low_stock_table.setHorizontalHeaderLabels(["Наименование", "Остаток", "Цена (руб.)", "Тип устройства"])
        reports_layout.addWidget(self.low_stock_table)

        load_low_stock_btn = QPushButton("Загрузить")
        load_low_stock_btn.clicked.connect(self.load_low_stock)
        reports_layout.addWidget(load_low_stock_btn)

        reports_layout.addWidget(QLabel("Неиспользованные мастера:"))
        self.idle_masters_table = QTableWidget()
        self.idle_masters_table.setColumnCount(2)
        self.idle_masters_table.setHorizontalHeaderLabels(["ФИО", "Контакт"])
        reports_layout.addWidget(self.idle_masters_table)

        load_idle_btn = QPushButton("Загрузить")
        load_idle_btn.clicked.connect(self.load_idle_masters)
        reports_layout.addWidget(load_idle_btn)

        reports_tab.setLayout(reports_layout)
        tabs.addTab(reports_tab, "Отчеты")

        layout.addWidget(tabs)
        self.setLayout(layout)
        self.load_staff()
        self.load_services()
        self.load_consumables()

    def load_staff(self):
        try:
            self.staff_table.setRowCount(0)
            users = self.db.query(User).all()
            for user in users:
                row = self.staff_table.rowCount()
                self.staff_table.insertRow(row)
                self.staff_table.setItem(row, 0, QTableWidgetItem(user.full_name))
                self.staff_table.setItem(row, 1, QTableWidgetItem(user.role.name))
                self.staff_table.setItem(row, 2, QTableWidgetItem(user.phone))
                self.staff_table.setItem(row, 3, QTableWidgetItem("Да" if user.is_active else "Нет"))
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка при загрузке персонала: {str(e)}")
            print(f"Staff error: {e}")

    def load_services(self):
        try:
            self.services_table.setRowCount(0)
            services = self.db.query(Service).all()
            for service in services:
                row = self.services_table.rowCount()
                self.services_table.insertRow(row)
                self.services_table.setItem(row, 0, QTableWidgetItem(service.name))
                self.services_table.setItem(row, 1, QTableWidgetItem(f"{service.price:.2f}"))
                self.services_table.setItem(row, 2, QTableWidgetItem(str(service.duration_minutes)))
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка при загрузке услуг: {str(e)}")
            print(f"Services error: {e}")

    def load_debtors(self):
        try:
            self.debtors_table.setRowCount(0)
            requests = get_unpaid_completed_requests(self.db)
            for req in requests:
                cost = calculate_repair_cost(self.db, req.id)
                row = self.debtors_table.rowCount()
                self.debtors_table.insertRow(row)
                self.debtors_table.setItem(row, 0, QTableWidgetItem(str(req.id)))
                self.debtors_table.setItem(row, 1, QTableWidgetItem(req.client.full_name))
                self.debtors_table.setItem(row, 2, QTableWidgetItem(f"{cost:.2f}"))
                self.debtors_table.setItem(row, 3, QTableWidgetItem(req.closed_at.strftime("%Y-%m-%d") if req.closed_at else ""))
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка при загрузке должников: {str(e)}")
            print(f"Debtors error: {e}")

    def load_low_stock(self):
        try:
            self.low_stock_table.setRowCount(0)
            consumables = get_low_stock_consumables(self.db)
            for c in consumables:
                row = self.low_stock_table.rowCount()
                self.low_stock_table.insertRow(row)
                self.low_stock_table.setItem(row, 0, QTableWidgetItem(c.name))
                self.low_stock_table.setItem(row, 1, QTableWidgetItem(str(c.quantity)))
                self.low_stock_table.setItem(row, 2, QTableWidgetItem(f"{c.price:.2f}"))
                self.low_stock_table.setItem(row, 3, QTableWidgetItem(c.device_type or ""))
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка при загрузке дефицита: {str(e)}")
            print(f"Low stock error: {e}")

    def load_idle_masters(self):
        try:
            self.idle_masters_table.setRowCount(0)
            masters = get_idle_masters(self.db)
            for m in masters:
                row = self.idle_masters_table.rowCount()
                self.idle_masters_table.insertRow(row)
                self.idle_masters_table.setItem(row, 0, QTableWidgetItem(m.user.full_name))
                self.idle_masters_table.setItem(row, 1, QTableWidgetItem(m.user.phone))
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка при загрузке мастеров: {str(e)}")
            print(f"Idle masters error: {e}")

    def add_staff(self):
        try:
            dialog = UserDialog(self.db)
            if dialog.exec() == dialog.DialogCode.Accepted:
                user = dialog.get_user_data()
                if user:
                    self.load_staff()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка при добавлении сотрудника: {str(e)}")
            print(f"Add staff error: {e}")

    def add_service(self):
        try:
            dialog = ServiceDialog(self.db)
            if dialog.exec() == dialog.DialogCode.Accepted:
                service = dialog.get_service_data()
                if service:
                    self.load_services()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка при добавлении услуги: {str(e)}")
            print(f"Add service error: {e}")

    def load_consumables(self):
        try:
            self.consumables_table.setRowCount(0)
            consumables = self.db.query(Consumable).all()
            for consumable in consumables:
                row = self.consumables_table.rowCount()
                self.consumables_table.insertRow(row)
                self.consumables_table.setItem(row, 0, QTableWidgetItem(consumable.name))
                self.consumables_table.setItem(row, 1, QTableWidgetItem(consumable.manufacturer or "-"))
                self.consumables_table.setItem(row, 2, QTableWidgetItem(f"{consumable.price:.2f}"))
                self.consumables_table.setItem(row, 3, QTableWidgetItem(str(consumable.quantity)))
                self.consumables_table.setItem(row, 4, QTableWidgetItem(consumable.device_type or "-"))
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка при загрузке расходников: {str(e)}")
            print(f"Consumables error: {e}")

    def add_consumable(self):
        try:
            from frontend.roles.dialogs.consumable_dialog import ConsumableDialog
            dialog = ConsumableDialog(self.db)
            if dialog.exec() == dialog.DialogCode.Accepted:
                consumable = dialog.get_consumable_data()
                if consumable:
                    self.load_consumables()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка при добавлении расходника: {str(e)}")
            print(f"Add consumable error: {e}")
