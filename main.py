from fastapi import FastAPI,Depends,HTTPException
import models
from router import auth
from fastapi.responses import JSONResponse
from models import Transactions
from database import engine,Base
from database import sessionlocal
from typing import Annotated,Literal
from sqlalchemy.orm import Session
from pydantic import BaseModel,Field
from typing import Optional
from pydantic import Field
from datetime import date as Date
from typing import Literal
from datetime import date
from router.auth import user_depency
models.Base.metadata.create_all(bind=engine)
app=FastAPI()
app.include_router(auth.router)
def get_db():
    db=sessionlocal()
    try:
        yield db
    finally:
        db.close()
db_dependency = Annotated[Session, Depends(get_db)]  
          
@app.get('/')
def get_transaction(db: db_dependency):

    transactions = db.query(Transactions).all()

    if not transactions:
        raise HTTPException(
            status_code=404,
            detail='No transactions found'
        )

    return transactions
  

class Transaction(BaseModel):
    title : str
    amount : float
    type : Literal['income','expense']
    category : str
    date : date


class TransactionUpdate(BaseModel):
    title: Optional[str] = None
    amount: Optional[float] = Field(default=None, gt=0)
    type: Optional[Literal["income", "expense"]] = None
    category: Optional[str] = None
    date: Optional[Date] = None
    
@app.post("/creat/")
def creat_transaction(
    user: user_depency,
    db: db_dependency,
    new_transaction: Transaction
):
    if user is None:
        raise HTTPException(
            status_code=401,
            detail='User not authenticated'
        )

    Transaction_model = Transactions(
        **new_transaction.model_dump(),
        owner_id=user.get('id')
    )

    db.add(Transaction_model)
    db.commit()
    db.refresh(Transaction_model)

    return Transaction_model
@app.get('/transaction/{id}/')
def specifique(
    user: user_depency,
    id: int,
    db: db_dependency
):

    if user is None:
        raise HTTPException(
            status_code=401,
            detail='User not authenticate'
        )

    specifique_transaction = db.query(Transactions).filter(
        Transactions.id == id,
        Transactions.owner_id == user.get('id')
    ).first()

    if specifique_transaction is None:
        raise HTTPException(
            status_code=404,
            detail='Transaction not found'
        )

    return specifique_transaction
        
@app.delete('/delete_transactions/{transaction_id}')
def delete_transaction(
    user: user_depency,
    transaction_id: int,
    db: db_dependency
):

    transaction = db.query(Transactions).filter(
        Transactions.id == transaction_id,
        Transactions.owner_id == user.get('id')
    ).first()

    if transaction is None:
        raise HTTPException(
            status_code=404,
            detail='Transaction not found'
        )

    db.delete(transaction)
    db.commit()

    return JSONResponse(
        status_code=200,
        content={
            "message": "Transaction deleted successfully"
        }
    )
        
@app.put('/update/{id}')
def udate_data(
    user: user_depency,
    id: int,
    db: db_dependency,
    update_record: TransactionUpdate
):

    if user is None:
        raise HTTPException(
            status_code=401,
            detail='User not authenticate'
        )

    transaction = db.query(Transactions).filter(
        Transactions.id == id,
        Transactions.owner_id == user.get('id')
    ).first()

    if transaction is None:
        raise HTTPException(
            status_code=404,
            detail='Not found Transaction.'
        )

    update_data = update_record.model_dump(exclude_unset=True)

    for key, value in update_data.items():
        setattr(transaction, key, value)

    db.commit()
    db.refresh(transaction)

    return JSONResponse(
        status_code=200,
        content={
            "message": "Successfully updated"
        }
    )
    
@app.get('/transactions/filter')
def filter_transactions(
    user: user_depency,
    db: db_dependency,
    type: Literal['income', 'expense'] | None = None,
    category: str | None = None,
    minimum_amount: float | None = None,
    maximum_amount: float | None = None
):

    if user is None:
        raise HTTPException(
            status_code=401,
            detail='User not authenticated'
        )

    query = db.query(Transactions).filter(
        Transactions.owner_id == user.get('id')
    )

    if type is not None:
        query = query.filter(
            Transactions.type == type
        )

    if category is not None:
        query = query.filter(
            Transactions.category == category
        )

    if minimum_amount is not None:
        query = query.filter(
            Transactions.amount >= minimum_amount
        )

    if maximum_amount is not None:
        query = query.filter(
            Transactions.amount <= maximum_amount
        )

    transactions = query.all()

    return transactions