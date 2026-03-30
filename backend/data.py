from sqlalchemy import create_engine, Column, Integer, String, Enum as SQLEnum
import sqlalchemy
from sqlalchemy.orm import sessionmaker, declarative_base, Session
from enum import Enum

engine = create_engine('sqlite:///mydata.db', echo=True)
Base = declarative_base()
session = sessionmaker(bind=engine)


class TransactionStatus(str, Enum):
    DRAFT = 'DRAFT'
    PROCESSING = 'PROCESSING'
    FROZEN = 'FROZEN'
    ARCHIVE = 'ARCHIVE'
class transaction (Base):
    __tablename__ = 'transaction'
    id  = Column(Integer, primary_key=True)
    status = Column(SQLEnum(TransactionStatus), default=TransactionStatus.DRAFT)
    sender = Column(String)
    receiver = Column(String)
    amount = Column(Integer)

Base.metadata.create_all(engine)


def get_db():
    db = session()
    try:
        yield db
    finally:
        db.close()
def create_trans(db:Session, sender:str, receiver:str, amount:int):
    new_trans = transaction(sender = sender, receiver = receiver, amount = amount)
    db.add(new_trans)
    db.commit()
    db.refresh(new_trans)
    return new_trans
def get_all_trans(db:Session):
    return db.query(transaction).all()
def get_trans(db:Session, trans_id:int):
    return db.query(transaction).filter(transaction.id == trans_id).first()
def update_trans(db:Session, db_trans:transaction, new_status: TransactionStatus):
    db_trans.status = new_status
    db.commit()
    db.refresh(db_trans)
    return db_trans
def delete_trans(db:Session, db_trans:transaction):
    db.delete(db_trans)
    db.commit()