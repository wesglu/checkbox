from fastapi import APIRouter, status, Body, HTTPException, Depends, Query
from typing import Annotated, Optional
import asyncio
import uuid
from fastapi.responses import PlainTextResponse
from tabulate import tabulate
import textwrap

from app import models
from app.core.config import settings
from app.api.deps import CurrentUser
from app import crud, models
from app.utils import get_receipt_text

router = APIRouter(prefix='/check')

@router.post(
    "/create", 
    status_code=status.HTTP_201_CREATED, 
    response_model=models.CheckResponse,
    summary="Create a new check",
    description="Creates a new check with the provided positions and payment details."
)
async def create_check(
    *,
    check: models.CheckRequest = Body(..., description="The check request containing positions and payment details"), 
    user: CurrentUser
):
    position_totals = [position.price * position.quantity for position in check.positions]
    total = sum(position_totals)
    rest = check.payment.amount - total

    if rest < 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Payment amount is less than the total price of the check")
    
    created_check = models.Check(
        user_id=user.id,
        total=total,
        rest=rest,
    )

    created_check = await crud.create_check(created_check)
    positions = [
        models.Position(
            **position.model_dump(),
            check_id=created_check.id,
            total=position.price * position.quantity
        )
        for position in check.positions
    ]
    payment = models.Payment(
        **check.payment.model_dump(),
        check_id=created_check.id,
    )

    tasks = [
        crud.create_positions(positions),
        crud.create_payment(payment),
    ]
    positions, payment = await asyncio.gather(*tasks)
    check = await crud.get_check_by_id(created_check.id)
    print(check)
    # Ensure the response includes all required fields
    response_model = models.CheckResponse(
        id=check.id,
        created_at=check.created_at,
        total=round(check.total, 2),
        rest=round(check.rest, 2),
        positions=check.positions, 
        payment=check.payment
    )
    response = response_model.model_validate(check)
    
    return response


@router.get(
    "/get-all", 
    response_model=list[models.CheckResponse],
    summary="Retrieve all checks",
    description="Retrieves all checks for the current user, with optional filters for date, total, and payment type."
)
async def get_all_checks(
    *,
    date_preset: models.DatePreset = Query(default="all", description="Date preset to filter checks by"),
    total_ge: Optional[float] = Query(default=None, description="Filter checks with total greater than this value"),
    total_le: Optional[float] = Query(default=None, description="Filter checks with total less than this value"),
    payment_type: Optional[models.PaymentType] = Query(default=None, description="Filter checks by payment type"),
    offset: Optional[int] = Query(default=0, description="Offset for pagination"),
    limit: Optional[int] = Query(default=100, description="Limit for pagination"),
    user: CurrentUser
) -> list[models.CheckResponse]:
    checks = await crud.get_all_users_checks(user.id, date_preset, total_ge, total_le, payment_type, offset, limit)
    if len(checks) == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No checks found")
    return checks

@router.get(
    "/get", 
    response_model=models.CheckResponse,
    summary="Retrieve a specific check",
    description="Retrieves a specific check by its ID for the current user."
)
async def get_check(
    *,
    check_id: uuid.UUID = Query(..., description="The UUID of the check to retrieve"),
    user: CurrentUser
) -> models.CheckResponse:
    check = await crud.get_check_by_id(check_id)
    if check is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Check not found")
    return check

@router.get(
    "/get-text", 
    response_class=PlainTextResponse,
    summary="Retrieve check text",
    description="Retrieves the text representation of a check by its ID."
)
async def get_check_text(
    check_id: uuid.UUID = Query(..., description="The UUID of the check to retrieve text for"),
) -> str:
    check = await crud.get_check_by_id(check_id)
    if check is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Check not found")
    
    receipt_text = get_receipt_text(check)
    
    return receipt_text

