from fastapi import FastAPI, status, HTTPException, Depends
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from data import get_db, create_trans, TransactionStatus, get_all_trans, get_trans, update_trans, delete_trans


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
    model_config = {"from_attributes": True}
class TransactionUpdateRequest(BaseModel):
    status: TransactionStatus
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)
@app.post(
    '/transactions',
    response_model = TransactionResponse,
    status_code = status.HTTP_201_CREATED,
)
def create_transaction(info:TransactionRequest, db: Session = Depends(get_db)):
    transaction = create_trans(
        db = db,
        sender = info.sender,
        receiver = info.receiver,
        amount = info.amount,
    )
    return transaction


@app.patch(
    '/transactions/{id}',
    response_model = TransactionResponse,
    status_code = status.HTTP_200_OK,
)
def api_update_transaction(id:int, update_data:TransactionUpdateRequest, db: Session = Depends(get_db)):
    db_trans = get_trans(db, trans_id=id)
    if not db_trans:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Транзакция с id {id} не найдена'.format(id=id),
        )
    if db_trans.status == TransactionStatus.ARCHIVE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Архивную транзакцию нельзя изменить"
        )
    elif db_trans.status == TransactionStatus.PROCESSING and update_data.status == TransactionStatus.DRAFT:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Нельзя вернуть в создание транзакцию, которая уже обрабатывается"
        )
    return update_trans(db, db_trans = db_trans, new_status=update_data.status)




@app.get(
    "/transactions",
    response_model = list[TransactionResponse],
)
def api_get_all_trans(db: Session = Depends(get_db)):
    return get_all_trans(db)
@app.get(
    '/transactions/{id}',
    response_model = TransactionResponse,
)
def api_get_trans(id: int, db: Session = Depends(get_db)):
    transaction1 = get_trans(db, trans_id=id)
    if not transaction1:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Транзакция с id {id} не найдена"
        )
    return transaction1

@app.delete(
    '/transactions/{id}',
    status_code = status.HTTP_204_NO_CONTENT,
)
def api_delete_trans(id: int, db: Session = Depends(get_db)):
    db_trans = get_trans(db, trans_id=id)
    if not db_trans:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail = f'Транзакция с id {id} не найдена'
        )
    delete_trans(db, db_trans = db_trans)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="localhost", port=8000)