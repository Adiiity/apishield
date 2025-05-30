from datetime import datetime, timezone
import os, enum
from sqlalchemy import DateTime, Float, create_engine, Column, String, Enum, Integer, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Fetch PostgreSQL credentials from .env
POSTGRES_USER = os.getenv("POSTGRES_USER")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")
POSTGRES_DB = os.getenv("POSTGRES_DB")
POSTGRES_HOST = os.getenv("POSTGRES_HOST")
POSTGRES_PORT = os.getenv("POSTGRES_PORT")

# Construct the DATABASE URL
DATABASE_URL = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"

# Create the PostgreSQL engine
engine = create_engine(DATABASE_URL)

# Session Factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Define Base for Models
Base = declarative_base()

class RoleEnum(str, enum.Enum):
    admin="admin"
    user="user"


# Define User Model
class User(Base):
    __tablename__ = "users"
    username = Column(String, primary_key=True, index=True)
    hashed_password = Column(String)
    role = Column(Enum(RoleEnum),default="user")

    transactions = relationship("Transaction", back_populates="user", cascade="all, delete-orphan")

class Transaction(Base):
    __tablename__="transactions"

    id=Column(Integer, primary_key=True, index= True, autoincrement=True)
    user_id= Column(String, ForeignKey("users.username"))
    amount= Column(Float, nullable=False)
    
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    user= relationship("User", back_populates="transactions")

# Create Tables
Base.metadata.drop_all(bind=engine)

Base.metadata.create_all(bind=engine)