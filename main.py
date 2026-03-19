from encodings.palmos import decoding_table
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
class TransactionUpdateRequest(BaseModel):
    status: TransactionStatus
app = FastAPI()
@app.post(
    '/transaction',
    response_model = TransactionResponse,
    status_code = status.HTTP_201_CREATED,
)
def create_transaction(info:TransactionRequest):
    id = len(trans) + 1
    transaction = TransactionResponse(
        id = id,
        sender = info.sender,
        receiver = info.receiver,
        amount = info.amount,
    )
    trans.append(transaction)
    return transaction


@app.patch(
    '/transaction/{id}',
    response_model = TransactionResponse,
    status_code = status.HTTP_200_OK,
)
def update_transaction(id:int, update_data:TransactionUpdateRequest):
    for transaction in trans:
        if transaction.id == id:
            if transaction.status == TransactionStatus.ARCHIVE:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Архивную транзакцию нельзя изменить"
                )
            elif transaction.status == TransactionStatus.PROCESSING and update_data.status == TransactionStatus.DRAFT:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Нельзя вернуть в создание транзакцию, которая уже обрабатывается"
                )
            transaction.status = update_data.status
            return transaction

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail='Транзакция с id {id} не найдена'.format(id=id),
    )



@app.get(
    "/transactions",
    response_model = list[TransactionResponse],
)
def get_transactions():
    return trans