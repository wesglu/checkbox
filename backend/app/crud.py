from sqlmodel import select
from sqlalchemy.orm import joinedload, selectinload
from fastapi import HTTPException, status
import uuid
from sqlalchemy import func
from datetime import datetime, timedelta

from app import models
from app.core.db import get_session

async def create_user(user: models.User):
    async with get_session() as session:
        check_stmt = select(models.User).where(models.User.login == user.login)
        result = await session.execute(check_stmt)
        if result.scalar_one_or_none():
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User already exists")
        else:
            session.add(user)
            await session.commit()
            await session.refresh(user)
            return user
        
async def create_positions(positions: list[models.Position]):
    async with get_session() as session:
        session.add_all(positions)
        await session.commit()
        for position in positions:
            await session.refresh(position)
        return positions
    
async def create_payment(payment: models.Payment):
    async with get_session() as session:
        session.add(payment)
        await session.commit()
        await session.refresh(payment)
        print("here3")
        return payment
    
async def create_check(check: models.Check):
    async with get_session() as session:
        session.add(check)
        await session.commit()
        await session.refresh(check)
        return check

async def get_check_by_id(check_id: uuid.UUID):
    async with get_session() as session:
        print(check_id)
        stmt = (
            select(models.Check)
            .where(models.Check.id == check_id)
            .options(joinedload(models.Check.positions), 
                     joinedload(models.Check.payment),
                     joinedload(models.Check.user)
                    )
        )
        result = await session.execute(stmt)
        return result.unique().scalars().one_or_none()
    
async def get_all_users_checks(
        user_id: int, 
        date_preset: models.DatePreset, 
        total_ge: float, 
        total_le: float, 
        payment_type: models.PaymentType, 
        offset: int, 
        limit: int
    ):
    async with get_session() as session:
        stmt = (
            select(models.Check)
            .join(models.Check.payment)
            .where(models.Check.user_id == user_id)
            .order_by(models.Check.created_at.desc())
            .options(selectinload(models.Check.positions), 
                     selectinload(models.Check.payment))
        )
        if date_preset == models.DatePreset.ALL:
            ...
        elif date_preset == models.DatePreset.TODAY:
            stmt = stmt.where(func.date(models.Check.created_at) == datetime.now().date())
        elif date_preset == models.DatePreset.LAST_3_DAYS:
            stmt = stmt.where(func.date(models.Check.created_at) >= (datetime.now() - timedelta(days=3)).date())
        elif date_preset == models.DatePreset.LAST_7_DAYS:
            stmt = stmt.where(func.date(models.Check.created_at) >= (datetime.now() - timedelta(days=7)).date())
        elif date_preset == models.DatePreset.LAST_MONTH:
            stmt = stmt.where(func.date(models.Check.created_at) >= (datetime.now() - timedelta(days=30)).date())
        elif date_preset == models.DatePreset.LAST_YEAR:
            stmt = stmt.where(func.date(models.Check.created_at) >= (datetime.now() - timedelta(days=365)).date())
        
        if total_ge:
            stmt = stmt.where(models.Check.total >= total_ge)
        if total_le:
            stmt = stmt.where(models.Check.total <= total_le)
        
        if payment_type:
            stmt = stmt.where(models.Payment.type == payment_type)
        
        stmt = stmt.offset(offset if offset is not None else 0)
        stmt = stmt.limit(limit if limit is not None else 100)
        print(str(stmt))
        result = await session.execute(stmt)
        return result.unique().scalars().all()

async def get_user_by_login(login: str):
    async with get_session() as session:
        stmt = select(models.User).where(models.User.login == login)
        result = await session.execute(stmt)
        user = result.scalar_one_or_none()
        if user is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        return user
    
async def get_public_user(user_id: int):
    async with get_session() as session:
        stmt = select(models.User).where(models.User.id == user_id)
        result = await session.execute(stmt)
        user = result.scalar_one()
        if user:
            return models.UserPublic.model_validate(user)
        else:
            return None
        
    