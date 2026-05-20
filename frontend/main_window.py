from PyQt6.QtWidgets import (
    QMainWindow, QStackedWidget, QMessageBox
)
from backend.database import SessionLocal
from backend.auth import get_user_role
from frontend.login_dialog import LoginDialog
from frontend.roles.operator_window import OperatorWindow
from frontend.roles.master_window import MasterWindow
from frontend.roles.admin_window import AdminWindow

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Сервис-Центр Компьютерной Техники")
        self.setGeometry(100, 100, 1200, 700)
        self.db = SessionLocal()
        self.current_user = None
        self.stacked_widget = QStackedWidget()
        self.setCentralWidget(self.stacked_widget)
        self.show_login()

    def show_login(self):
        login_dialog = LoginDialog()
        if login_dialog.exec() == LoginDialog.DialogCode.Accepted:
            self.current_user = login_dialog.get_current_user()
            if self.current_user:
                self.load_role_interface()
            else:
                QMessageBox.critical(self, "Ошибка", "Ошибка аутентификации")
                self.close()
        else:
            self.close()

    def load_role_interface(self):
        role = get_user_role(self.db, self.current_user.id)

        # Remove previous widget if exists
        while self.stacked_widget.count() > 0:
            self.stacked_widget.removeWidget(self.stacked_widget.widget(0))

        if role == "Администратор":
            self.role_widget = AdminWindow(self.current_user, self.db)
        elif role == "Оператор-приемщик":
            self.role_widget = OperatorWindow(self.current_user, self.db)
        elif role == "Мастер по ремонту":
            self.role_widget = MasterWindow(self.current_user, self.db)
        else:
            QMessageBox.critical(self, "Ошибка", "Неизвестная роль пользователя")
            self.close()
            return

        self.stacked_widget.addWidget(self.role_widget)
        self.show()

    def closeEvent(self, event):
        self.db.close()
        event.accept()
