"""
Database initialization script with sample data
Run this once to set up the database schema and populate with initial data
"""

from backend.database import engine, SessionLocal, Base
from backend.models import (
    Role, User, Master, RequestStatus, RequestPriority, RepairType,
    Service, Client, Device, RepairRequest, RequestMaster, WorkRecord,
    WorkRecordService, Consumable, WorkRecordConsumable, Attachment
)
from backend.auth import hash_password
from datetime import datetime

def init_database():
    # Create all tables
    Base.metadata.create_all(bind=engine)
    print("✓ Tables created")

    db = SessionLocal()

    # Insert Roles
    roles = [
        Role(name="Администратор"),
        Role(name="Оператор-приемщик"),
        Role(name="Мастер по ремонту")
    ]
    db.add_all(roles)
    db.commit()
    print("✓ Roles inserted")

    # Insert Request Statuses
    statuses = [
        RequestStatus(name="Новая"),
        RequestStatus(name="На выполнении"),
        RequestStatus(name="Приостановлена"),
        RequestStatus(name="Выполнена"),
        RequestStatus(name="Отменена")
    ]
    db.add_all(statuses)
    db.commit()
    print("✓ Request statuses inserted")

    # Insert Priorities
    priorities = [
        RequestPriority(name="Низкий"),
        RequestPriority(name="Обычный"),
        RequestPriority(name="Высокий")
    ]
    db.add_all(priorities)
    db.commit()
    print("✓ Priorities inserted")

    # Insert Repair Types
    repair_types = [
        RepairType(name="Диагностика"),
        RepairType(name="Замена комплектующих"),
        RepairType(name="Сервисное обслуживание"),
        RepairType(name="Восстановление данных"),
        RepairType(name="Переустановка ОС")
    ]
    db.add_all(repair_types)
    db.commit()
    print("✓ Repair types inserted")

    # Insert Services
    services = [
        Service(name="Диагностика", price=500, duration_minutes=30, is_available=True),
        Service(name="Замена экрана", price=2000, duration_minutes=60, is_available=True),
        Service(name="Замена батареи", price=1500, duration_minutes=30, is_available=True),
        Service(name="Чистка от пыли", price=800, duration_minutes=45, is_available=True),
        Service(name="Переустановка ОС", price=1200, duration_minutes=90, is_available=True),
        Service(name="Замена жесткого диска", price=2500, duration_minutes=60, is_available=True)
    ]
    db.add_all(services)
    db.commit()
    print("✓ Services inserted")

    # Insert Users (Admin, Operator, Masters)
    admin_role = db.query(Role).filter(Role.name == "Администратор").first()
    operator_role = db.query(Role).filter(Role.name == "Оператор-приемщик").first()
    master_role = db.query(Role).filter(Role.name == "Мастер по ремонту").first()

    users = [
        User(
            full_name="Администратор Иван",
            phone="+79001234567",
            password_hash=hash_password("admin123"),
            is_active=True,
            role_id=admin_role.id
        ),
        User(
            full_name="Оператор Ольга",
            phone="+79009876543",
            password_hash=hash_password("operator123"),
            is_active=True,
            role_id=operator_role.id
        ),
        User(
            full_name="Мастер Петр",
            phone="+79005555555",
            password_hash=hash_password("master123"),
            is_active=True,
            role_id=master_role.id
        ),
        User(
            full_name="Мастер Сергей",
            phone="+79006666666",
            password_hash=hash_password("master123"),
            is_active=True,
            role_id=master_role.id
        )
    ]
    db.add_all(users)
    db.commit()
    print("✓ Users inserted")

    # Create Master profiles for users with master role
    master_user_1 = db.query(User).filter(User.phone == "+79005555555").first()
    master_user_2 = db.query(User).filter(User.phone == "+79006666666").first()

    masters = [
        Master(user_id=master_user_1.id, is_active=True),
        Master(user_id=master_user_2.id, is_active=True)
    ]
    db.add_all(masters)
    db.commit()
    print("✓ Masters inserted")

    # Insert Clients
    clients = [
        Client(
            full_name="Сидоров Иван",
            phone="+79101111111",
            birth_date=datetime(1990, 5, 15).date(),
            passport_series="4501",
            passport_number="123456",
            passport_issued_by="УФМС г. Москвы",
            passport_issue_date=datetime(2015, 3, 10).date()
        ),
        Client(
            full_name="Петрова Мария",
            phone="+79102222222",
            birth_date=datetime(1995, 8, 20).date(),
            passport_series="4502",
            passport_number="654321",
            passport_issued_by="УФМС г. Спб",
            passport_issue_date=datetime(2016, 6, 15).date()
        ),
        Client(
            full_name="Козлов Александр",
            phone="+79103333333",
            birth_date=datetime(1988, 12, 25).date(),
            passport_series="4503",
            passport_number="789456",
            passport_issued_by="УФМС г. Казани",
            passport_issue_date=datetime(2014, 9, 20).date()
        )
    ]
    db.add_all(clients)
    db.commit()
    print("✓ Clients inserted")

    # Insert Devices
    client_1 = db.query(Client).filter(Client.phone == "+79101111111").first()
    client_2 = db.query(Client).filter(Client.phone == "+79102222222").first()

    devices = [
        Device(
            device_type="Ноутбук",
            model_name="Dell Inspiron 15",
            serial_number="ABC123DEF456",
            client_id=client_1.id
        ),
        Device(
            device_type="Смартфон",
            model_name="iPhone 12",
            serial_number="XYZ789UVW000",
            client_id=client_2.id
        ),
        Device(
            device_type="Ноутбук",
            model_name="HP Pavilion 17",
            serial_number="HP987654321",
            client_id=client_1.id
        )
    ]
    db.add_all(devices)
    db.commit()
    print("✓ Devices inserted")

    # Insert Consumables
    consumables = [
        Consumable(
            manufacturer="Samsung",
            name="SSD 500GB",
            device_type="Ноутбук",
            price=2500,
            quantity=10
        ),
        Consumable(
            manufacturer="Kingston",
            name="RAM 8GB DDR4",
            device_type="Ноутбук",
            price=2000,
            quantity=5
        ),
        Consumable(
            manufacturer="Apple",
            name="Экран iPhone 12",
            device_type="Смартфон",
            price=5000,
            quantity=2
        ),
        Consumable(
            manufacturer="Unknown",
            name="Батарея ноутбука",
            device_type="Ноутбук",
            price=3000,
            quantity=0
        ),
        Consumable(
            manufacturer="Qualcomm",
            name="Зарядный кабель",
            device_type="Смартфон",
            price=500,
            quantity=15
        )
    ]
    db.add_all(consumables)
    db.commit()
    print("✓ Consumables inserted")

    # Insert Sample Repair Requests
    operator_user = db.query(User).filter(User.phone == "+79009876543").first()
    new_status = db.query(RequestStatus).filter(RequestStatus.name == "Новая").first()
    high_priority = db.query(RequestPriority).filter(RequestPriority.name == "Высокий").first()
    normal_priority = db.query(RequestPriority).filter(RequestPriority.name == "Обычный").first()
    diagnosis_type = db.query(RepairType).filter(RepairType.name == "Диагностика").first()

    requests = [
        RepairRequest(
            problem_description="Ноутбук не включается",
            client_id=client_1.id,
            device_id=devices[0].id,
            created_by_user_id=operator_user.id,
            status_id=new_status.id,
            priority_id=high_priority.id,
            repair_type_id=diagnosis_type.id,
            created_at=datetime.utcnow()
        ),
        RepairRequest(
            problem_description="Экран разбит",
            client_id=client_2.id,
            device_id=devices[1].id,
            created_by_user_id=operator_user.id,
            status_id=new_status.id,
            priority_id=normal_priority.id,
            repair_type_id=diagnosis_type.id,
            created_at=datetime.utcnow()
        )
    ]
    db.add_all(requests)
    db.commit()
    print("✓ Sample repair requests inserted")

    # Assign masters to requests
    master_1 = db.query(Master).first()
    if requests and master_1:
        assignment = RequestMaster(
            repair_request_id=requests[0].id,
            master_id=master_1.id
        )
        db.add(assignment)
        db.commit()
        print("✓ Masters assigned to requests")

    db.close()
    print("\n✅ Database initialization completed successfully!")

if __name__ == "__main__":
    init_database()
