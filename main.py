from enum import Enum
from http.client import responses

from fastapi import FastAPI, status, HTTPException
from pydantic import BaseModel
from enum import Enum

trans = []
class TransactionStatus (str, Enum):
    DRAFT = 'DRAFT'
    PROCESSING = 'PROCESSING'
    FROZEN = 'FROZEN'
    ARCHIVE = 'ARCHIVE'
class TransactionRequest(BaseModel):
    sender: str
    receiver: str
    amount: int
class TransactionResponse (BaseModel):
    sender: str
    receiver: str
    amount: int
    status: TransactionStatus = TransactionStatus.DRAFT
    id: int

app = FastAPI()
@app.post(
    '/transaction',
    response_model = TransactionResponse,
    status_code = status.HTTP_201_CREATED,
)
def create_transaction(info:TransactionRequest):
    id = len(trans) + 1
    transaction = TransactionResponse(
        sender = info.sender,
        receiver = info.receiver,
        amount = info.amount,
    )
    trans.append(transaction)
    return transaction

