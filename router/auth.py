from fastapi import FastAPI,Depends,HTTPException,APIRouter
import models
from fastapi.responses import JSONResponse
from models import Transactions,Users
from database import engine,Base
from database import sessionlocal
from typing import Annotated,Literal
from sqlalchemy.orm import Session
from pydantic import BaseModel,Field
from datetime import datetime,timedelta,timezone
from passlib.context import CryptContext
from jose import jwt
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer

SECRET_KEY='8bc7b636f2359aed642ae10799b0d8a5dc17d26adde223e9550239f3fc69c308'
ALGORITHM = "HS256"
models.Base.metadata.create_all(bind=engine)
bcrypt_context=CryptContext(schemes=['bcrypt'],deprecated='auto')
OAuth2_bearer = OAuth2PasswordBearer(tokenUrl='login')

def get_current_user(token: Annotated[str, Depends(OAuth2_bearer)]):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get('sub')
        user_id: int = payload.get('id')
        if username is None or user_id is None:
            raise HTTPException(status_code=401, detail='User un authorized')
        return {'username': username, 'id': user_id}
    except HTTPException:
        raise 
    except Exception:
        raise HTTPException(status_code=401,detail='Could not validate user')
    
    
def get_db():
    db=sessionlocal()
    try:
        yield db
    finally:
        db.close()
db_dependency = Annotated[Session, Depends(get_db)]  
router=APIRouter()

class CreatUser(BaseModel):
    email :str
    username : str
    password : str
    
@router.post('/creat_user/')
def creat_user(db:db_dependency,new_user:CreatUser):
    
    user_model=Users(email=new_user.email,
                     username=new_user.username,
                     hash_password=bcrypt_context.hash(new_user.password))
    db.add(user_model)
    db.commit()
    db.refresh(user_model)
    return JSONResponse(status_code=200,content='Created Successfully')


def authenticate_user(username,db,password):
    user=db.query(Users).filter(Users.username==username).first()
    if user is None:
        return False
    if bcrypt_context.verify(password,user.hash_password):
        return user
    return False
        
def create_access_token(username: str, user_id: int,expires_delta: timedelta):
    encode = {'sub': username, 'id': user_id}
    expires = datetime.now(timezone.utc) + expires_delta
    encode.update({'exp': expires})
    return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)        
@router.post('/login')
def login_user(db : db_dependency, form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    
    user = authenticate_user(form_data.username,db,form_data.password) 
    if not user:
       raise HTTPException(
        status_code=401,
        detail="Could not validate user"
    )
    
    token = create_access_token(user.username, user.id,timedelta(minutes=30))
    return {'access_token': token, 'token_type': 'bearer'}    
    
    
    
user_depency=Annotated[dict,Depends(get_current_user)]