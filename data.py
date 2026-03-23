from sqlalchemy import create_engine, Column, Integer, String, Enum as SQLEnum
import sqlalchemy
from sqlalchemy.orm import sessionmaker, declarative_base
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
