from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTabWidget, QTableWidget,
    QTableWidgetItem, QMessageBox, QLabel, QLineEdit
)
from PyQt6.QtCore import Qt
from backend.queries import (
    get_unpaid_completed_requests, get_low_stock_consumables,
    get_idle_masters, get_cancelled_requests_last_month
)

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
        self.staff_table.setHorizontalHeaderLabels(["ФИО", "Роль", "Активен", ""])
        staff_layout.addWidget(self.staff_table)

        staff_tab.setLayout(staff_layout)
        tabs.addTab(staff_tab, "Персонал")

        # Вкладка: Справочники
        reference_tab = QWidget()
        reference_layout = QVBoxLayout()

        reference_layout.addWidget(QLabel("Управление услугами:"))
        self.services_table = QTableWidget()
        self.services_table.setColumnCount(3)
        self.services_table.setHorizontalHeaderLabels(["Название", "Цена", ""])
        reference_layout.addWidget(self.services_table)

        add_service_btn = QPushButton("Добавить услугу")
        add_service_btn.clicked.connect(self.add_service)
        reference_layout.addWidget(add_service_btn)

        reference_tab.setLayout(reference_layout)
        tabs.addTab(reference_tab, "Справочники")

        # Вкладка: Отчеты
        reports_tab = QWidget()
        reports_layout = QVBoxLayout()

        # Должники
        reports_layout.addWidget(QLabel("Должники:"))
        self.debtors_table = QTableWidget()
        self.debtors_table.setColumnCount(4)
        self.debtors_table.setHorizontalHeaderLabels(["ID заявки", "Клиент", "Сумма", "Дата"])
        reports_layout.addWidget(self.debtors_table)

        load_debtors_btn = QPushButton("Загрузить должников")
        load_debtors_btn.clicked.connect(self.load_debtors)
        reports_layout.addWidget(load_debtors_btn)

        # Низкий остаток
        reports_layout.addWidget(QLabel("Дефицит склада:"))
        self.low_stock_table = QTableWidget()
        self.low_stock_table.setColumnCount(4)
        self.low_stock_table.setHorizontalHeaderLabels(["Наименование", "Остаток", "Цена", ""])
        reports_layout.addWidget(self.low_stock_table)

        load_low_stock_btn = QPushButton("Загрузить")
        load_low_stock_btn.clicked.connect(self.load_low_stock)
        reports_layout.addWidget(load_low_stock_btn)

        # Неиспользованные мастера
        reports_layout.addWidget(QLabel("Неиспользованные мастера:"))
        self.idle_masters_table = QTableWidget()
        self.idle_masters_table.setColumnCount(2)
        self.idle_masters_table.setHorizontalHeaderLabels(["ФИО", ""])
        reports_layout.addWidget(self.idle_masters_table)

        load_idle_btn = QPushButton("Загрузить")
        load_idle_btn.clicked.connect(self.load_idle_masters)
        reports_layout.addWidget(load_idle_btn)

        reports_tab.setLayout(reports_layout)
        tabs.addTab(reports_tab, "Отчеты")

        layout.addWidget(tabs)
        self.setLayout(layout)

    def load_debtors(self):
        try:
            self.debtors_table.setRowCount(0)
            requests = get_unpaid_completed_requests(self.db)
            for req in requests:
                from backend.queries import calculate_repair_cost
                cost = calculate_repair_cost(self.db, req.id)
                row = self.debtors_table.rowCount()
                self.debtors_table.insertRow(row)
                self.debtors_table.setItem(row, 0, QTableWidgetItem(str(req.id)))
                self.debtors_table.setItem(row, 1, QTableWidgetItem(req.client.full_name))
                self.debtors_table.setItem(row, 2, QTableWidgetItem(f"{cost:.2f} ₽"))
                self.debtors_table.setItem(row, 3, QTableWidgetItem(req.closed_at.strftime("%Y-%m-%d")))
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
                self.low_stock_table.setItem(row, 2, QTableWidgetItem(f"{c.price:.2f} ₽"))
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
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка при загрузке мастеров: {str(e)}")
            print(f"Idle masters error: {e}")

    def add_staff(self):
        QMessageBox.information(self, "Информация", "Функция добавления сотрудника в разработке")

    def add_service(self):
        QMessageBox.information(self, "Информация", "Функция добавления услуги в разработке")
