from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey, DECIMAL, Date
from sqlalchemy.orm import relationship
from backend.database import Base

class Role(Base):
    __tablename__ = "roles"
    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True, nullable=False)
    users = relationship("User", back_populates="role")

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    full_name = Column(String(100), nullable=False)
    phone = Column(String(20), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    last_auth_at = Column(DateTime)
    role_id = Column(Integer, ForeignKey("roles.id", ondelete="RESTRICT"), nullable=False)

    role = relationship("Role", back_populates="users")
    master = relationship("Master", back_populates="user", uselist=False)
    repair_requests = relationship("RepairRequest", back_populates="created_by", foreign_keys="RepairRequest.created_by_user_id")

class Master(Base):
    __tablename__ = "masters"
    id = Column(Integer, primary_key=True)
    is_active = Column(Boolean, default=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)

    user = relationship("User", back_populates="master")
    request_assignments = relationship("RequestMaster", back_populates="master")
    work_records = relationship("WorkRecord", back_populates="master")

class RequestStatus(Base):
    __tablename__ = "request_statuses"
    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True, nullable=False)
    repair_requests = relationship("RepairRequest", back_populates="status")

class RequestPriority(Base):
    __tablename__ = "request_priorities"
    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True, nullable=False)
    repair_requests = relationship("RepairRequest", back_populates="priority")

class RepairType(Base):
    __tablename__ = "repair_types"
    id = Column(Integer, primary_key=True)
    name = Column(String(100), unique=True, nullable=False)
    repair_requests = relationship("RepairRequest", back_populates="repair_type")

class Service(Base):
    __tablename__ = "services"
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    price = Column(DECIMAL(10, 2), nullable=False)
    duration_minutes = Column(Integer, nullable=False)
    is_available = Column(Boolean, default=True)
    work_record_services = relationship("WorkRecordService", back_populates="service")

class Client(Base):
    __tablename__ = "clients"
    id = Column(Integer, primary_key=True)
    full_name = Column(String(100), nullable=False)
    birth_date = Column(Date)
    phone = Column(String(20), nullable=False)
    passport_series = Column(String(10))
    passport_number = Column(String(20))
    passport_issued_by = Column(String(200))
    passport_issue_date = Column(Date)

    devices = relationship("Device", back_populates="client")
    repair_requests = relationship("RepairRequest", back_populates="client")

class Device(Base):
    __tablename__ = "devices"
    id = Column(Integer, primary_key=True)
    device_type = Column(String(50), nullable=False)
    serial_number = Column(String(100), nullable=False)
    model_name = Column(String(100), nullable=False)
    client_id = Column(Integer, ForeignKey("clients.id", ondelete="CASCADE"), nullable=False)

    client = relationship("Client", back_populates="devices")
    repair_requests = relationship("RepairRequest", back_populates="device")

class RepairRequest(Base):
    __tablename__ = "repair_requests"
    id = Column(Integer, primary_key=True)
    problem_description = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    closed_at = Column(DateTime)
    is_paid = Column(Boolean, default=False)
    client_id = Column(Integer, ForeignKey("clients.id", ondelete="RESTRICT"), nullable=False)
    device_id = Column(Integer, ForeignKey("devices.id", ondelete="RESTRICT"), nullable=False)
    created_by_user_id = Column(Integer, ForeignKey("users.id", ondelete="RESTRICT"), nullable=False)
    status_id = Column(Integer, ForeignKey("request_statuses.id", ondelete="RESTRICT"), nullable=False)
    priority_id = Column(Integer, ForeignKey("request_priorities.id", ondelete="RESTRICT"), nullable=False)
    repair_type_id = Column(Integer, ForeignKey("repair_types.id", ondelete="RESTRICT"), nullable=False)

    client = relationship("Client", back_populates="repair_requests")
    device = relationship("Device", back_populates="repair_requests")
    created_by = relationship("User", back_populates="repair_requests", foreign_keys=[created_by_user_id])
    status = relationship("RequestStatus", back_populates="repair_requests")
    priority = relationship("RequestPriority", back_populates="repair_requests")
    repair_type = relationship("RepairType", back_populates="repair_requests")
    masters = relationship("RequestMaster", back_populates="repair_request")
    work_records = relationship("WorkRecord", back_populates="repair_request")

class RequestMaster(Base):
    __tablename__ = "request_masters"
    id = Column(Integer, primary_key=True)
    assigned_at = Column(DateTime, default=datetime.utcnow)
    repair_request_id = Column(Integer, ForeignKey("repair_requests.id", ondelete="CASCADE"), nullable=False)
    master_id = Column(Integer, ForeignKey("masters.id", ondelete="CASCADE"), nullable=False)

    repair_request = relationship("RepairRequest", back_populates="masters")
    master = relationship("Master", back_populates="request_assignments")

class WorkRecord(Base):
    __tablename__ = "work_records"
    id = Column(Integer, primary_key=True)
    work_description = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    repair_request_id = Column(Integer, ForeignKey("repair_requests.id", ondelete="CASCADE"), nullable=False)
    master_id = Column(Integer, ForeignKey("masters.id", ondelete="RESTRICT"), nullable=False)

    repair_request = relationship("RepairRequest", back_populates="work_records")
    master = relationship("Master", back_populates="work_records")
    services = relationship("WorkRecordService", back_populates="work_record")
    consumables = relationship("WorkRecordConsumable", back_populates="work_record")
    attachments = relationship("Attachment", back_populates="work_record")

class WorkRecordService(Base):
    __tablename__ = "work_record_services"
    id = Column(Integer, primary_key=True)
    work_record_id = Column(Integer, ForeignKey("work_records.id", ondelete="CASCADE"), nullable=False)
    service_id = Column(Integer, ForeignKey("services.id", ondelete="RESTRICT"), nullable=False)

    work_record = relationship("WorkRecord", back_populates="services")
    service = relationship("Service", back_populates="work_record_services")

class Consumable(Base):
    __tablename__ = "consumables"
    id = Column(Integer, primary_key=True)
    manufacturer = Column(String(100))
    name = Column(String(200), nullable=False)
    device_type = Column(String(50))
    price = Column(DECIMAL(10, 2), nullable=False)
    quantity = Column(Integer, default=0)
    work_records = relationship("WorkRecordConsumable", back_populates="consumable")

class WorkRecordConsumable(Base):
    __tablename__ = "work_record_consumables"
    id = Column(Integer, primary_key=True)
    quantity_used = Column(Integer, nullable=False)
    work_record_id = Column(Integer, ForeignKey("work_records.id", ondelete="CASCADE"), nullable=False)
    consumable_id = Column(Integer, ForeignKey("consumables.id", ondelete="RESTRICT"), nullable=False)

    work_record = relationship("WorkRecord", back_populates="consumables")
    consumable = relationship("Consumable", back_populates="work_records")

class Attachment(Base):
    __tablename__ = "attachments"
    id = Column(Integer, primary_key=True)
    file_path = Column(String(500), nullable=False)
    uploaded_at = Column(DateTime, default=datetime.utcnow)
    work_record_id = Column(Integer, ForeignKey("work_records.id", ondelete="CASCADE"), nullable=False)

    work_record = relationship("WorkRecord", back_populates="attachments")
