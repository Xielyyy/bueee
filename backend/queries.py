from datetime import datetime, timedelta
from sqlalchemy import and_, or_, func
from sqlalchemy.orm import Session
from backend.models import (
    RepairRequest, Client, Device, User, Master, WorkRecord,
    RequestStatus, RequestPriority, Service, Consumable, WorkRecordConsumable
)

# ===== CLIENT QUERIES =====
def search_clients(db: Session, phone: str = None, full_name: str = None):
    query = db.query(Client)
    if phone:
        query = query.filter(Client.phone.contains(phone))
    if full_name:
        query = query.filter(Client.full_name.contains(full_name))
    return query.all()

def create_client(db: Session, full_name: str, phone: str, birth_date=None,
                 passport_series=None, passport_number=None, passport_issued_by=None,
                 passport_issue_date=None) -> Client:
    client = Client(
        full_name=full_name,
        phone=phone,
        birth_date=birth_date,
        passport_series=passport_series,
        passport_number=passport_number,
        passport_issued_by=passport_issued_by,
        passport_issue_date=passport_issue_date
    )
    db.add(client)
    db.commit()
    db.refresh(client)
    return client

# ===== DEVICE QUERIES =====
def create_device(db: Session, device_type: str, serial_number: str, model_name: str, client_id: int) -> Device:
    device = Device(
        device_type=device_type,
        serial_number=serial_number,
        model_name=model_name,
        client_id=client_id
    )
    db.add(device)
    db.commit()
    db.refresh(device)
    return device

def get_client_devices(db: Session, client_id: int):
    return db.query(Device).filter(Device.client_id == client_id).all()

# ===== REPAIR REQUEST QUERIES =====
def create_repair_request(db: Session, problem_description: str, client_id: int, device_id: int,
                         created_by_user_id: int, status_id: int, priority_id: int, repair_type_id: int) -> RepairRequest:
    request = RepairRequest(
        problem_description=problem_description,
        client_id=client_id,
        device_id=device_id,
        created_by_user_id=created_by_user_id,
        status_id=status_id,
        priority_id=priority_id,
        repair_type_id=repair_type_id
    )
    db.add(request)
    db.commit()
    db.refresh(request)
    return request

def get_repair_request(db: Session, request_id: int) -> RepairRequest:
    return db.query(RepairRequest).filter(RepairRequest.id == request_id).first()

def get_all_requests(db: Session, start_date: datetime = None, end_date: datetime = None):
    query = db.query(RepairRequest)
    if start_date:
        query = query.filter(RepairRequest.created_at >= start_date)
    if end_date:
        query = query.filter(RepairRequest.created_at <= end_date)
    return query.order_by(RepairRequest.created_at.desc()).all()

def update_repair_request_status(db: Session, request_id: int, status_id: int):
    request = db.query(RepairRequest).filter(RepairRequest.id == request_id).first()
    if request:
        request.status_id = status_id
        if status_id == db.query(RequestStatus).filter(RequestStatus.name == "Выполнена").first().id:
            request.closed_at = datetime.utcnow()
        db.commit()

# ===== MASTER QUERIES =====
def get_master_requests(db: Session, master_id: int):
    return db.query(RepairRequest).join(
        RepairRequest.masters
    ).filter(
        RepairRequest.masters.any(master_id=master_id)
    ).all()

def get_active_masters(db: Session):
    return db.query(Master).filter(Master.is_active == True).all()

# ===== CONSUMABLES QUERIES =====
def get_consumables_by_device_type(db: Session, device_type: str):
    return db.query(Consumable).filter(Consumable.device_type == device_type).all()

def get_all_consumables(db: Session):
    return db.query(Consumable).all()

def get_consumable_by_id(db: Session, consumable_id: int):
    return db.query(Consumable).filter(Consumable.id == consumable_id).first()

def update_consumable_quantity(db: Session, consumable_id: int, quantity_change: int):
    consumable = db.query(Consumable).filter(Consumable.id == consumable_id).first()
    if consumable:
        consumable.quantity += quantity_change
        if consumable.quantity < 0:
            raise ValueError(f"Insufficient stock: {consumable.name}")
        db.commit()

def deduct_consumable(db: Session, consumable_id: int, quantity: int):
    consumable = db.query(Consumable).filter(Consumable.id == consumable_id).first()
    if not consumable or consumable.quantity < quantity:
        raise ValueError(f"Not enough stock for {consumable.name}")
    consumable.quantity -= quantity
    db.commit()

# ===== WORK RECORDS QUERIES =====
def create_work_record(db: Session, work_description: str, repair_request_id: int, master_id: int) -> WorkRecord:
    record = WorkRecord(
        work_description=work_description,
        repair_request_id=repair_request_id,
        master_id=master_id
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return record

def get_work_records(db: Session, repair_request_id: int):
    return db.query(WorkRecord).filter(WorkRecord.repair_request_id == repair_request_id).all()

# ===== REPORTING QUERIES =====
def get_unpaid_completed_requests(db: Session):
    """Выгрузка должников: все выполненные заявки, которые не оплачены"""
    completed_status = db.query(RequestStatus).filter(RequestStatus.name == "Выполнена").first()
    return db.query(RepairRequest).filter(
        and_(
            RepairRequest.status_id == completed_status.id,
            RepairRequest.is_paid == False
        )
    ).all()

def get_low_stock_consumables(db: Session, critical_level: int = 5):
    """Контроль дефицита склада: запчасти с остатком ≤ критической отметки"""
    return db.query(Consumable).filter(Consumable.quantity <= critical_level).all()

def get_idle_masters(db: Session):
    """Мониторинг эффективности: мастера без активных заявок"""
    active_status = db.query(RequestStatus).filter(RequestStatus.name.in_(["Новая", "На выполнении"])).all()
    active_status_ids = [s.id for s in active_status]

    masters_with_active_requests = db.query(Master).join(
        Master.request_assignments
    ).join(
        RepairRequest
    ).filter(
        RepairRequest.status_id.in_(active_status_ids)
    ).distinct().all()

    all_masters = db.query(Master).filter(Master.is_active == True).all()
    idle_masters = [m for m in all_masters if m not in masters_with_active_requests]
    return idle_masters

def get_cancelled_requests_last_month(db: Session):
    """Анализ отмененных заказов за последний месяц"""
    cancelled_status = db.query(RequestStatus).filter(RequestStatus.name == "Отменена").first()
    month_ago = datetime.utcnow() - timedelta(days=30)

    return db.query(RepairRequest).filter(
        and_(
            RepairRequest.status_id == cancelled_status.id,
            RepairRequest.created_at >= month_ago
        )
    ).all()

def calculate_repair_cost(db: Session, repair_request_id: int) -> float:
    """Динамический расчет стоимости ремонта"""
    work_records = db.query(WorkRecord).filter(WorkRecord.repair_request_id == repair_request_id).all()

    total_service_cost = 0
    total_consumable_cost = 0

    for record in work_records:
        # Сумма услуг
        for service_record in record.services:
            total_service_cost += float(service_record.service.price)

        # Сумма расходников
        for consumable_record in record.consumables:
            cost = float(consumable_record.consumable.price) * consumable_record.quantity_used
            total_consumable_cost += cost

    return total_service_cost + total_consumable_cost

def get_completed_requests_by_date_range(db: Session, start_date: datetime, end_date: datetime):
    """Получить завершенные заявки за период"""
    completed_status = db.query(RequestStatus).filter(RequestStatus.name == "Выполнена").first()
    return db.query(RepairRequest).filter(
        and_(
            RepairRequest.status_id == completed_status.id,
            RepairRequest.closed_at >= start_date,
            RepairRequest.closed_at <= end_date
        )
    ).all()

def get_master_performance(db: Session, master_id: int):
    """Получить статистику работы мастера"""
    work_records = db.query(WorkRecord).filter(WorkRecord.master_id == master_id).all()
    completed_requests = db.query(RepairRequest).join(
        RepairRequest.masters
    ).filter(
        and_(
            RepairRequest.masters.any(master_id=master_id),
            RepairRequest.status_id == db.query(RequestStatus).filter(RequestStatus.name == "Выполнена").first().id
        )
    ).count()

    return {
        "work_records_count": len(work_records),
        "completed_requests": completed_requests,
        "total_cost": sum([calculate_repair_cost(db, r.id) for r in [wr.repair_request for wr in work_records]])
    }

def get_average_repair_time(db: Session, days: int = 30):
    """Получить среднее время ремонта за последние N дней"""
    from sqlalchemy import func
    start_date = datetime.utcnow() - timedelta(days=days)

    completed_status = db.query(RequestStatus).filter(RequestStatus.name == "Выполнена").first()

    results = db.query(
        func.avg(func.julianday(RepairRequest.closed_at) - func.julianday(RepairRequest.created_at)).label("avg_days")
    ).filter(
        and_(
            RepairRequest.status_id == completed_status.id,
            RepairRequest.closed_at >= start_date
        )
    ).first()

    return results.avg_days if results and results.avg_days else 0

def get_revenue_by_master(db: Session):
    """Получить доход по мастерам"""
    masters = db.query(Master).filter(Master.is_active == True).all()
    revenue_data = {}

    for master in masters:
        requests = db.query(RepairRequest).join(
            RepairRequest.masters
        ).filter(
            RepairRequest.masters.any(master_id=master.id)
        ).all()

        total = sum([calculate_repair_cost(db, r.id) for r in requests])
        revenue_data[master.user.full_name] = total

    return revenue_data
