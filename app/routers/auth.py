from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
from app.core.config import settings
from app.core.database import db
from app.models.schemas import UserCreate, UserLogin, Token, UserResponse, MessageResponse, UserUpdate
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
    
    # 检查邮箱是否已存在
    existing_email = db.execute_one("SELECT id FROM users WHERE email = %s", (user.email,))
    if existing_email:
        raise HTTPException(status_code=400, detail="邮箱已存在")
    
    # 检查身份证是否已存在
    existing_id_card = db.execute_one("SELECT id FROM users WHERE id_card = %s", (user.id_card,))
    if existing_id_card:
        raise HTTPException(status_code=400, detail="身份证号已存在")
    
    # 创建新用户
    hashed_password = get_password_hash(user.password)
    user_id = db.execute_insert(
        """INSERT INTO users (username, nickname, password, email, phone, id_card, real_name, gender, age, company, user_type) 
           VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
        (user.username, user.nickname, hashed_password, user.email, user.phone, 
         user.id_card, user.real_name, user.gender, user.age, user.company, user.user_type)
    )
    
    return MessageResponse(message="注册成功")

@router.post("/login", response_model=Token)
async def login(user_credentials: UserLogin):
    # 支持邮箱或用户名登录
    user = db.execute_one("SELECT * FROM users WHERE email = %s OR username = %s", 
                         (user_credentials.email, user_credentials.email))
    if not user or not verify_password(user_credentials.password, user["password"]):
        raise HTTPException(status_code=401, detail="邮箱或密码错误")
    
    access_token = create_access_token(data={"sub": user["username"]})
    
    # 返回用户信息
    user_response = UserResponse(
        id=user["id"],
        username=user["username"],
        nickname=user["nickname"],
        email=user["email"],
        phone=user["phone"],
        real_name=user["real_name"],
        gender=user["gender"],
        age=user["age"],
        avatar=user.get("avatar"),
        signature=user.get("signature"),
        vip_level=user.get("vip_level", 0),
        company=user.get("company"),
        user_type=user.get("user_type", "passenger"),
        created_at=user["created_at"]
    )
    
    return Token(access_token=access_token, token_type="bearer", user=user_response)

@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: dict = Depends(get_current_user)):
    return UserResponse(
        id=current_user["id"],
        username=current_user["username"],
        nickname=current_user["nickname"],
        email=current_user["email"],
        phone=current_user["phone"],
        real_name=current_user["real_name"],
        gender=current_user["gender"],
        age=current_user["age"],
        avatar=current_user.get("avatar"),
        signature=current_user.get("signature"),
        vip_level=current_user.get("vip_level", 0),
        company=current_user.get("company"),
        user_type=current_user.get("user_type", "passenger"),
        created_at=current_user["created_at"]
    )

@router.put("/me", response_model=UserResponse)
async def update_user_info(
    user_update: UserUpdate,
    current_user: dict = Depends(get_current_user)
):
    """更新用户信息"""
    update_fields = []
    update_values = []
    
    for field, value in user_update.dict(exclude_unset=True).items():
        if value is not None:
            update_fields.append(f"{field} = %s")
            update_values.append(value)
    
    if not update_fields:
        raise HTTPException(status_code=400, detail="没有提供要更新的字段")
    
    update_values.append(current_user["id"])
    query = f"UPDATE users SET {', '.join(update_fields)} WHERE id = %s"
    db.execute_update(query, tuple(update_values))
    
    # 返回更新后的用户信息
    updated_user = db.execute_one("SELECT * FROM users WHERE id = %s", (current_user["id"],))
    return UserResponse(
        id=updated_user["id"],
        username=updated_user["username"],
        nickname=updated_user["nickname"],
        email=updated_user["email"],
        phone=updated_user["phone"],
        real_name=updated_user["real_name"],
        gender=updated_user["gender"],
        age=updated_user["age"],
        avatar=updated_user.get("avatar"),
        signature=updated_user.get("signature"),
        vip_level=updated_user.get("vip_level", 0),
        company=updated_user.get("company"),
        user_type=updated_user.get("user_type", "passenger"),
        created_at=updated_user["created_at"]
    ) 