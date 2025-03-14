from datetime import datetime, timezone
from fastapi import Depends, FastAPI, HTTPException, Request
from pydantic import BaseModel
from fastapi.security import OAuth2PasswordBearer

from fastapi.openapi.models import OAuthFlows as OAuthFlowsModel
from fastapi.openapi.models import SecurityScheme as SecuritySchemeModel
from fastapi.openapi.utils import get_openapi

from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.middleware import SlowAPIMiddleware
from auth import get_user,create_user, get_db, create_access_token, verify_password, get_user_from_token
from database import Transaction, User
from sqlalchemy.orm import Session

app=FastAPI()

# Rate limiter setup
limiter=Limiter(key_func=get_remote_address)
app.state.limiter = limiter

app.add_middleware(SlowAPIMiddleware)

# OAuth2 Setup
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login", scheme_name="JWT")

class LoginRequest(BaseModel):
    username: str
    password: str

class TransactionCreate(BaseModel):
    amount: float

class TransactionResponse(BaseModel):
    id: int
    user_id: str
    amount: float
    timestamp: datetime

@app.get("/")
async def root():
    return {"message": "API is running!"}

# Register new user
@app.post("/auth/register")
async def register(request: LoginRequest, db: Session = Depends(get_db)):
    existing_user = get_user(db, request.username)
    if existing_user:
        raise HTTPException(status_code=400, detail="User already exists")
    
    user = create_user(db, request.username, request.password)
    return {"message": "User created successfully", "user": user.username}

@app.post("/auth/login")
@limiter.limit("5/minute") # Login atempts limiter
async def login(request:Request, body: LoginRequest, db: Session = Depends(get_db)):
    user= get_user(db, body.username)
    if not user or not verify_password(body.password, user.hashed_password ):
        raise HTTPException(status_code=401, detail="Invalid Credentials")
    
    access_token=create_access_token({"sub": user.username})
    return {"access_token": access_token, "token-type":"Bearer"}

# Restrict Admin Routes
@app.get("/admin/users")
async def get_all_users(db: Session = Depends(get_db), token: str = Depends(OAuth2PasswordBearer(tokenUrl="auth/login"))):
    user=get_user_from_token(token,db)

    if user.role!='admin':
        raise HTTPException(status_code=403, detail="Not authorized")

    users = db.query(User).all()
    return [{"username": u.username, "role": u.role} for u in users]



# protected route
@app.get("/users/me")
async def read_users_me(token: str = Depends(oauth2_scheme)):
    # return {"user": "John Doe"}
    return {"message": "This is a protected route"}

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="SecureAPI",
        version="1.0.0",
        description="JWT Authentication with FastAPI",
        routes=app.routes,
    )
    openapi_schema["components"]["securitySchemes"] = {
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
        }
    }
    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi

@app.post("/transactions", response_model=TransactionResponse)
async def create_transaction(
    transaction: TransactionCreate,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)
):
    user = get_user_from_token(token, db)

    new_transaction = Transaction(
        user_id=user.username, 
        amount=transaction.amount, 
        timestamp=datetime.now(timezone.utc)
    )

    db.add(new_transaction)
    db.commit()
    db.refresh(new_transaction)

    return new_transaction

@app.get("/transactions", response_model=list[TransactionResponse])
async def get_transactions(
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)
):
    user = get_user_from_token(token, db)

    transactions = db.query(Transaction).filter(Transaction.user_id == user.username).all()
    
    return transactions


# app.include_router(app)
