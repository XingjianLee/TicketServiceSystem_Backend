from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
from app.core.config import settings
from app.core.database import db
from app.models.schemas import UserCreate, UserLogin, Token, UserResponse, MessageResponse
import uuid

router = APIRouter()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)
    return encoded_jwt

def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    user = db.execute_one("SELECT * FROM users WHERE username = %s", (username,))
    if user is None:
        raise credentials_exception
    return user

@router.post("/register", response_model=MessageResponse)
async def register(user: UserCreate):
    # 检查用户名是否已存在
    existing_user = db.execute_one("SELECT id FROM users WHERE username = %s", (user.username,))
    if existing_user:
        raise HTTPException(status_code=400, detail="用户名已存在")
    
    # 检查身份证是否已存在
    existing_id_card = db.execute_one("SELECT id FROM users WHERE id_card = %s", (user.id_card,))
    if existing_id_card:
        raise HTTPException(status_code=400, detail="身份证号已存在")
    
    # 创建新用户
    hashed_password = get_password_hash(user.password)
    user_id = db.execute_insert(
        """INSERT INTO users (username, nickname, password, email, phone, id_card, real_name, gender, age) 
           VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)""",
        (user.username, user.nickname, hashed_password, user.email, user.phone, 
         user.id_card, user.real_name, user.gender, user.age)
    )
    
    return MessageResponse(message="注册成功")

@router.post("/login", response_model=Token)
async def login(user_credentials: UserLogin):
    user = db.execute_one("SELECT * FROM users WHERE username = %s", (user_credentials.username,))
    if not user or not verify_password(user_credentials.password, user["password"]):
        raise HTTPException(status_code=401, detail="用户名或密码错误")
    
    access_token = create_access_token(data={"sub": user["username"]})
    return Token(access_token=access_token, token_type="bearer")

@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: dict = Depends(get_current_user)):
    return UserResponse(**current_user) 