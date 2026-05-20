import bcrypt
from sqlalchemy.orm import Session
from backend.models import User, Role

def hash_password(password: str) -> str:
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode(), salt).decode()

def verify_password(password: str, password_hash: str) -> bool:
    return bcrypt.checkpw(password.encode(), password_hash.encode())

def authenticate_user(db: Session, phone: str, password: str) -> User | None:
    user = db.query(User).filter(User.phone == phone).first()
    if not user or not user.is_active:
        return None
    if not verify_password(password, user.password_hash):
        return None
    return user

def get_user_role(db: Session, user_id: int) -> str | None:
    user = db.query(User).filter(User.id == user_id).first()
    if user and user.role:
        return user.role.name
    return None
