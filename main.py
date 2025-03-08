from fastapi import Depends, FastAPI, HTTPException, Request
from pydantic import BaseModel
from fastapi.security import OAuth2PasswordBearer

from fastapi.openapi.models import OAuthFlows as OAuthFlowsModel
from fastapi.openapi.models import SecurityScheme as SecuritySchemeModel
from fastapi.openapi.utils import get_openapi

from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.middleware import SlowAPIMiddleware
from auth import create_access_token, verify_password, hash_password

app=FastAPI()

# Rate limiter setup
limiter=Limiter(key_func=get_remote_address)
app.state.limiter = limiter


app.add_middleware(SlowAPIMiddleware)

# Dummy user database
fake_users_db = {
    "user@example.com": {
        "username": "user@example.com",
        "hashed_password": hash_password("securepassword"),
    }
}

# OAuth2 Setup
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login", scheme_name="JWT")

class LoginRequest(BaseModel):
    username: str
    password: str

@app.get("/")
async def root():
    return {"message": "API is running!"}

@app.post("/auth/login")
@limiter.limit("5/minute")  # Limit login attempts
async def login(request: Request, body: LoginRequest):  # Fix: Added `request: Request`
    user = fake_users_db.get(body.username)
    if not user or not verify_password(body.password, user["hashed_password"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    access_token = create_access_token(data={"sub": body.username})
    return {"access_token": access_token, "token_type": "Bearer"}

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