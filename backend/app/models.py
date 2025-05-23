from sqlmodel import SQLModel, Field, Relationship
from pydantic import BaseModel
from datetime import datetime, timezone
from enum import Enum
from typing import Optional, List
import uuid

# Enums
class PaymentType(str, Enum):
    CASH = "cash"
    CASHLESS = "cashless"

class DatePreset(str, Enum):
    ALL = "all"
    TODAY = "today"
    LAST_3_DAYS = "last_3_days"
    LAST_7_DAYS = "last_7_days"
    LAST_MONTH = "last_month"
    LAST_YEAR = "last_year"

##### USER MODELS #####
class UserPublic(SQLModel):
    id: int
    name: str
    login: str
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
        arbitrary_types_allowed = True

class User(SQLModel, table=True):
    __tablename__ = "users"

    id: int = Field(default=None, primary_key=True)
    name: str
    login: str
    password: str
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default=datetime.now(timezone.utc).replace(tzinfo=None))
    updated_at: datetime = Field(default=datetime.now(timezone.utc).replace(tzinfo=None))
    
    checks: Optional[list["Check"]] = Relationship(back_populates="user")

##### CHECK MODELS #####
class PositionBase(SQLModel):
    name: str = Field(..., description="Name of the position")
    price: float = Field(..., ge=0.01, description="Price of the position")
    quantity: int = Field(..., ge=1, description="Quantity of the position")

class PositionResponse(PositionBase):
    total: float

class Position(PositionBase, table=True):
    __tablename__ = "positions"

    id: int = Field(default=None, primary_key=True)
    total: float = Field(ge=0.01)

    check_id: uuid.UUID = Field(foreign_key="checks.id")
    check: "Check" = Relationship(back_populates="positions")
    

class PaymentBase(SQLModel):
    type: str = Field(..., description="Type of payment")
    amount: float = Field(..., ge=0.01, description="Amount of payment")

class PaymentResponse(PaymentBase):
    ...

class Payment(PaymentBase, table=True):
    __tablename__ = "payments"

    id: int = Field(default=None, primary_key=True)
    check_id: uuid.UUID = Field(foreign_key="checks.id")
    check: "Check" = Relationship(back_populates="payment")

class CheckRequest(SQLModel):
    positions: List[PositionBase] = Field(..., description="List of positions in the check")
    payment: PaymentBase = Field(..., description="Payment details for the check")


class Check(SQLModel, table=True):
    __tablename__ = "checks"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    positions: Optional[list[Position]] = Relationship(back_populates="check")
    payment: Optional[Payment] = Relationship(back_populates="check")
    total: float = Field(ge=0.01)
    rest: float = Field(ge=0.00)
    created_at: datetime = Field(default=datetime.now(timezone.utc).replace(tzinfo=None))
    
    user_id: int = Field(foreign_key="users.id")
    user: "User" = Relationship(back_populates="checks")

class CheckResponse(SQLModel):
    id: uuid.UUID
    positions: list[PositionResponse]
    payment: PaymentResponse
    total: float = Field(ge=0.01)
    rest: float = Field(ge=0.00)
    created_at: datetime

    class Config:
        from_attributes = True
        arbitrary_types_allowed = True

##### OTHER #####
class TokenPayload(SQLModel):
    sub: str
    exp: datetime
