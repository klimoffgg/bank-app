import enum

from sqlalchemy import create_engine, Column, Integer, String, Enum as SQLEnum, ForeignKey
import sqlalchemy
from sqlalchemy.orm import sessionmaker, declarative_base, Session, relationship
from enum import Enum

engine = create_engine('sqlite:///mydata.db', echo=True)
Base = declarative_base()
session = sessionmaker(bind=engine)

class TransactionStatus(str, Enum):
    DRAFT = 'DRAFT'
    PROCESSING = 'PROCESSING'
    FROZEN = 'FROZEN'
    ARCHIVE = 'ARCHIVE'

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)

    transactions = relationship("Transaction", back_populates="owner")

class Transaction(Base):
    __tablename__ = 'transactions'

    id = Column(Integer, primary_key=True, index=True)
    sender = Column(String, nullable=False)
    receiver = Column(String, nullable=False)
    amount = Column(Integer, nullable=False)
    status = Column(Enum(TransactionStatus), nullable=False)

    owner_id = Column(Integer, ForeignKey('users.id'))

    owner = relationship("User", back_populates="transactions")

def get_db():
    db = session()
    try:
        yield db
    finally:
        db.close()

def get_user_by_username(db: Session, username: str):
    return db.query(User).filter(User.username == username).first()
def create_user(db: Session, username: str, hashed_password: str):
    new_user = User(username = username,hashed_password = hashed_password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user
def create_trans(db: Session, sender: str, receiver: str, amount: int, owner_id: int):
    new_trans = Transaction(sender = sender, receiver = receiver, amount = amount, owner_id = owner_id)
    db.add(new_trans)
    db.commit()
    db.refresh(new_trans)
    return new_trans
def get_all_trans(db: Session):
    return db.query(Transaction).all()
def get_transaction_by_id(db: Session, trans_id: int):
    return db.query(Transaction).filter(Transaction.id == trans_id).first()
def delete_trans(db: Session, db_trans: Transaction):
    db.delete(db_trans)
    db.commit()
def update_trans(db: Session, new_trans: Transaction, new_status: TransactionStatus):
    new_trans.status = new_status
    db.commit()
    db.refresh(new_trans)
    return new_trans