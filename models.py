from database import Base
from sqlalchemy import Column,Integer,String,Boolean,ForeignKey,Enum,Float,Date
import enum
class Users(Base):
    
    __tablename__='users'
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String)
    username = Column(String, unique=True)
    hash_password = Column(String)
class TransactionType(enum.Enum):
    income = "income"
    expense = "expense"

    
class Transactions(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    amount = Column(Float)
    type = Column(Enum(TransactionType))
    category = Column(String)
    date = Column(Date)
    owner_id = Column(Integer, ForeignKey("users.id"))


    