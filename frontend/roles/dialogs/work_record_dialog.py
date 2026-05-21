from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QTextEdit, QListWidget, QListWidgetItem,
    QSpinBox, QPushButton, QMessageBox, QComboBox, QTabWidget, QWidget
)
from PyQt6.QtCore import Qt
from backend.queries import create_work_record
from backend.models import Consumable, WorkRecordConsumable, Service, WorkRecordService


class WorkRecordDialog(QDialog):
    def __init__(self, db, master_id, repair_request_id):
        super().__init__()
        self.db = db
        self.master_id = master_id
        self.repair_request_id = repair_request_id
        self.selected_consumables = {}
        self.selected_services = {}
        self.setWindowTitle("Добавить запись о работе")
        self.setGeometry(100, 100, 700, 600)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()

        layout.addWidget(QLabel("Описание работы:"))
        self.work_text = QTextEdit()
        self.work_text.setMinimumHeight(80)
        layout.addWidget(self.work_text)

        tabs = QTabWidget()

        # Вкладка: Запчасти
        consumables_tab = QWidget()
        consumables_layout = QVBoxLayout()

        consumables_layout.addWidget(QLabel("Использованные запчасти:"))
        self.consumables_list = QListWidget()
        consumables_layout.addWidget(self.consumables_list)

        consumables_add_layout = QHBoxLayout()
        self.consumable_combo = QComboBox()
        consumables = self.db.query(Consumable).all()
        for c in consumables:
            self.consumable_combo.addItem(f"{c.name} - {c.quantity} шт", c.id)
        consumables_add_layout.addWidget(QLabel("Запчасть:"))
        consumables_add_layout.addWidget(self.consumable_combo)

        self.qty_spin = QSpinBox()
        self.qty_spin.setMinimum(1)
        consumables_add_layout.addWidget(QLabel("Кол-во:"))
        consumables_add_layout.addWidget(self.qty_spin)

        add_consumable_btn = QPushButton("Добавить запчасть")
        add_consumable_btn.clicked.connect(self.add_consumable_to_list)
        consumables_add_layout.addWidget(add_consumable_btn)
        consumables_layout.addLayout(consumables_add_layout)

        remove_consumable_btn = QPushButton("Удалить выбранную")
        remove_consumable_btn.clicked.connect(self.remove_consumable_from_list)
        consumables_layout.addWidget(remove_consumable_btn)

        consumables_tab.setLayout(consumables_layout)
        tabs.addTab(consumables_tab, "Запчасти")

        # Вкладка: Услуги
        services_tab = QWidget()
        services_layout = QVBoxLayout()

        services_layout.addWidget(QLabel("Оказанные услуги:"))
        self.services_list = QListWidget()
        services_layout.addWidget(self.services_list)

        services_add_layout = QHBoxLayout()
        self.service_combo = QComboBox()
        services = self.db.query(Service).filter(Service.is_available == True).all()
        for s in services:
            self.service_combo.addItem(f"{s.name} - {s.price} руб.", s.id)
        services_add_layout.addWidget(QLabel("Услуга:"))
        services_add_layout.addWidget(self.service_combo)

        add_service_btn = QPushButton("Добавить услугу")
        add_service_btn.clicked.connect(self.add_service_to_list)
        services_add_layout.addWidget(add_service_btn)
        services_layout.addLayout(services_add_layout)

        remove_service_btn = QPushButton("Удалить выбранную")
        remove_service_btn.clicked.connect(self.remove_service_from_list)
        services_layout.addWidget(remove_service_btn)

        services_tab.setLayout(services_layout)
        tabs.addTab(services_tab, "Услуги")

        layout.addWidget(tabs)

        buttons = QHBoxLayout()
        ok_btn = QPushButton("Сохранить")
        ok_btn.clicked.connect(self.save_work_record)
        cancel_btn = QPushButton("Отмена")
        cancel_btn.clicked.connect(self.reject)
        buttons.addWidget(ok_btn)
        buttons.addWidget(cancel_btn)

        layout.addLayout(buttons)
        self.setLayout(layout)

    def add_consumable_to_list(self):
        consumable_id = self.consumable_combo.currentData()
        if consumable_id:
            qty = self.qty_spin.value()
            consumable = self.db.query(Consumable).filter(Consumable.id == consumable_id).first()
            if consumable:
                item_text = f"{consumable.name} x{qty}"
                item = QListWidgetItem(item_text)
                item.setData(Qt.ItemDataRole.UserRole, (consumable_id, qty))
                self.consumables_list.addItem(item)
                self.selected_consumables[consumable_id] = qty

    def remove_consumable_from_list(self):
        current_item = self.consumables_list.currentItem()
        if current_item:
            data = current_item.data(Qt.ItemDataRole.UserRole)
            if data:
                consumable_id = data[0]
                del self.selected_consumables[consumable_id]
            self.consumables_list.takeItem(self.consumables_list.row(current_item))

    def add_service_to_list(self):
        service_id = self.service_combo.currentData()
        if service_id:
            service = self.db.query(Service).filter(Service.id == service_id).first()
            if service:
                item_text = f"{service.name} ({service.price} руб.)"
                item = QListWidgetItem(item_text)
                item.setData(Qt.ItemDataRole.UserRole, service_id)
                self.services_list.addItem(item)
                self.selected_services[service_id] = service_id

    def remove_service_from_list(self):
        current_item = self.services_list.currentItem()
        if current_item:
            service_id = current_item.data(Qt.ItemDataRole.UserRole)
            if service_id in self.selected_services:
                del self.selected_services[service_id]
            self.services_list.takeItem(self.services_list.row(current_item))

    def save_work_record(self):
        work_description = self.work_text.toPlainText().strip()
        if not work_description:
            QMessageBox.warning(self, "Ошибка", "Заполните описание работы")
            return

        try:
            from backend.queries import deduct_consumable
            record = create_work_record(
                self.db,
                work_description=work_description,
                repair_request_id=self.repair_request_id,
                master_id=self.master_id
            )

            for consumable_id, qty in self.selected_consumables.items():
                consumable = self.db.query(Consumable).filter(Consumable.id == consumable_id).first()
                if consumable and consumable.quantity >= qty:
                    work_record_consumable = WorkRecordConsumable(
                        work_record_id=record.id,
                        consumable_id=consumable_id,
                        quantity_used=qty
                    )
                    self.db.add(work_record_consumable)
                    consumable.quantity -= qty
                else:
                    QMessageBox.warning(self, "Ошибка", f"Недостаточно запчасти {consumable.name}")
                    return

            for service_id in self.selected_services.keys():
                work_record_service = WorkRecordService(
                    work_record_id=record.id,
                    service_id=service_id
                )
                self.db.add(work_record_service)

            self.db.commit()
            QMessageBox.information(self, "Успех", "Запись о работе добавлена")
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка при сохранении: {str(e)}")
            self.db.rollback()
            print(f"Error: {e}")
