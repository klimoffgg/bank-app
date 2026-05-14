import os
from sys import prefix
from datetime import datetime, timedelta, timezone
from fastapi import FastAPI, status, HTTPException, Depends, security
from fastapi.security import HTTPBearer
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from new_data import get_db, get_user_by_username, create_user, create_trans, get_all_trans, get_transaction_by_id, delete_trans, update_trans
from dotenv import load_dotenv
from jose import JWTError, jwt

load_dotenv()

RT_SECRET_KEY = os.getenv('RT_SECRET_KEY')
AT_SECRET_KEY = os.getenv('AT_SECRET_KEY')

class Tokens:
    ALGORITHM = 'HS256'
    REFRESH_TOKEN_EXPIRE_DAYS = 7
    REFRESH_TOKEN_EXPIRE_TIMEDELTA = timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    ACCESS_TOKEN_EXPIRE_MINUTES = 15
    ACCESS_TOKEN_EXPIRE_TIMEDELTA = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    @classmethod
    def encode(cls, payload: dict, sk: str) -> str:
        return jwt.encode(payload, sk, algorithm=cls.ALGORITHM)
    @classmethod
    def decode (cls, token: str, sk: str) -> dict | None:
        try:
            return jwt.decode(token, sk, algorithms=[cls.ALGORITHM])
        except JWTError as ex:
            return None
    @classmethod
    def create_refresh_token(cls, user_id: int) -> str:
        iat = datetime.now(timezone.utc)
        exp = iat + cls.REFRESH_TOKEN_EXPIRE_TIMEDELTA
        payload = {
            "sub": str(user_id),
            "type": "refresh",
            "exp": exp,
            "iat": iat,
        }
        return cls.encode(payload, RT_SECRET_KEY)
    @classmethod
    def create_access_token(cls, user_id: int):
        iat = datetime.now(timezone.utc)
        exp = iat + cls.ACCESS_TOKEN_EXPIRE_TIMEDELTA
        payload = {
            "sub": str(user_id),
            "type": "access",
            "exp": exp,
            "iat": iat,
        }
        return cls.encode(payload, AT_SECRET_KEY)

    @classmethod
    def get_user_id_from_refresh_token(cls, token: str) -> int|None:
        payload = cls.decode(token, RT_SECRET_KEY)
        if not payload:
            return None

        if payload["type"] != "refresh":
            return None

        exp = datetime.fromtimestamp(payload["exp"], tz=timezone.utc)
        if exp < datetime.now(timezone.utc):
            return None

        return int(payload["sub"])

    @classmethod
    def get_user_id_from_access_token(cls, token: str) -> int|None:
        payload = cls.decode(token, AT_SECRET_KEY)
        if not payload:
            return None

        if payload["type"] != "access":
            return None
        exp = datetime.fromtimestamp(payload["exp"], tz=timezone.utc)
        if exp < datetime.now(timezone.utc):
            return None

        return int(payload["sub"])

security = HTTPBearer()

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
app = FastAPI(root_path = '/api')

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