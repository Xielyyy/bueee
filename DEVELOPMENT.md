# 🔨 Quickstart & Development Guide

## Первый запуск

```bash
# 1. Установить зависимости
pip install -r requirements.txt

# 2. Настроить .env (параметры MySQL)
# Пример:
# DB_HOST=localhost
# DB_PORT=3306
# DB_NAME=service_repair
# DB_USER=root
# DB_PASSWORD=your_password

# 3. Создать БД в MySQL
# CREATE DATABASE IF NOT EXISTS service_repair;

# 4. Инициализировать таблицы и тестовые данные
python init_db.py

# 5. Запустить приложение
python main.py
```

## 🧑‍💻 Добавление новой функции

### Пример 1: Добавить новый отчет в админ-интерфейс

**Шаг 1** — Добавить запрос в `backend/queries.py`:
```python
def get_revenue_by_master(db: Session):
    """Выручка по каждому мастеру"""
    return db.query(Master).all()  # и логика расчета
```

**Шаг 2** — Добавить кнопку и таблицу в `frontend/roles/admin_window.py`:
```python
load_revenue_btn = QPushButton("Выручка мастеров")
load_revenue_btn.clicked.connect(self.load_revenue)
reports_layout.addWidget(load_revenue_btn)
```

**Шаг 3** — Реализовать обработчик:
```python
def load_revenue(self):
    self.revenue_table.setRowCount(0)
    data = get_revenue_by_master(self.db)
    for item in data:
        # populate table
```

### Пример 2: Добавить новое поле в модель

**Шаг 1** — Добавить колонку в БД вручную:
```sql
ALTER TABLE repair_requests ADD COLUMN warranty_valid BOOLEAN DEFAULT FALSE;
```

**Шаг 2** — Добавить поле в модель `backend/models.py`:
```python
class RepairRequest(Base):
    ...
    warranty_valid = Column(Boolean, default=False)
```

**Шаг 3** — Использовать в запросах и интерфейсах

## 🐛 Частые задачи

### Добавить новую роль
1. Добавить в `init_db.py`: `Role(name="Новая роль")`
2. Создать новое окно `frontend/roles/new_role_window.py`
3. Обновить диспетчер в `frontend/main_window.py`

### Изменить прайс-лист
**Для администратора:**
1. Отредактировать таблицу услуг в админ-интерфейсе
2. Сохранить в БД через ORM в `backend/queries.py`

### Добавить новую запчасть
```python
from backend.database import SessionLocal
from backend.models import Consumable

db = SessionLocal()
new_part = Consumable(
    name="SSD 1TB",
    manufacturer="Samsung",
    price=5000,
    quantity=10
)
db.add(new_part)
db.commit()
db.close()
```

### Просмотреть все заявки через SQL
```sql
SELECT 
    rr.id,
    c.full_name,
    rr.problem_description,
    rs.name as status,
    rr.created_at
FROM repair_requests rr
JOIN clients c ON rr.client_id = c.id
JOIN request_statuses rs ON rr.status_id = rs.id
ORDER BY rr.created_at DESC;
```

## 📊 Отчеты в базе данных

Все отчеты реализованы в `backend/queries.py`:

### 1. Должники (неоплаченные завершенные)
```python
get_unpaid_completed_requests(db)
```

### 2. Дефицит склада (≤5 шт)
```python
get_low_stock_consumables(db, critical_level=5)
```

### 3. Неиспользованные мастера (без активных заявок)
```python
get_idle_masters(db)
```

### 4. Отмены за месяц
```python
get_cancelled_requests_last_month(db)
```

## 🔐 Управление пользователями

### Добавить сотрудника
```python
from backend.auth import hash_password
from backend.database import SessionLocal
from backend.models import User, Role

db = SessionLocal()
operator_role = db.query(Role).filter(Role.name == "Оператор-приемщик").first()

new_user = User(
    full_name="Новый Оператор",
    phone="+79001112233",
    password_hash=hash_password("password123"),
    role_id=operator_role.id,
    is_active=True
)
db.add(new_user)
db.commit()
```

### Заблокировать пользователя
```python
user = db.query(User).filter(User.phone == "+79001234567").first()
user.is_active = False
db.commit()
```

### Изменить пароль
```python
from backend.auth import hash_password

user = db.query(User).filter(User.phone == "+79001234567").first()
user.password_hash = hash_password("new_password")
db.commit()
```

## 🧪 Тестирование интерфейсов

Каждому окну соответствует роль. Для теста используйте тестовые учетные записи:

| Роль | Телефон | Пароль |
|------|---------|--------|
| Admin | +79001234567 | admin123 |
| Operator | +79009876543 | operator123 |
| Master | +79005555555 | master123 |

## 📝 Структура кода

```
backend/
├── config.py          # Параметры подключения
├── database.py        # SQLAlchemy session
├── models.py          # 15 ORM моделей
├── auth.py            # Хеширование, аутентификация
└── queries.py         # CRUD + отчеты

frontend/
├── main_window.py     # Главное окно, диспетчер
├── login_dialog.py    # Вход
└── roles/
    ├── operator_window.py    # Интерфейс оператора
    ├── master_window.py      # Интерфейс мастера
    ├── admin_window.py       # Интерфейс админа
    └── dialogs/              # Диалоги добавления
```

## 🚨 Частые ошибки

❌ **SQLAlchemy session not closed** → Используйте `db.close()` после операций  
❌ **Foreign key error** → Проверьте, что связанная запись существует  
❌ **Password verification fails** → Убедитесь, что используется `bcrypt.checkpw()`  
❌ **UI не обновляется** → Вызовите `self.load_data()` после изменения БД  

## 💡 Советы

- Всегда используйте ORM модели вместо raw SQL для безопасности
- Валидируйте входные данные в диалогах перед сохранением
- Используйте транзакции (`db.commit()`) после изменений
- Проверяйте `is_active` для пользователей и мастеров
- Рассчитывайте динамическую стоимость только при нужде (не кешируйте)

---

**Нужна помощь? Посмотрите соответствующий файл в `backend/` или `frontend/`**
