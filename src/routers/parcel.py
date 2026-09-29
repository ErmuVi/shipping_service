import uuid
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from src.database import get_async_session
from src.models import Parcel, ParcelType
from src.schemas.parcel import ParcelCreate, ParcelResponse
from src.worker import calculate_delivery_task

router = APIRouter(prefix="/parcels", tags=["Parcels"])


@router.post("")
async def create_parcel(
    parcel_data: ParcelCreate,
    request: Request,
    db: AsyncSession = Depends(get_async_session),
):
    type_check = await db.execute(
        select(ParcelType).where(ParcelType.id == parcel_data.type_id)
    )
    if not type_check.scalars().first():
        raise HTTPException(
            status_code=400, detail="Указанный тип посылки не существует"
        )

    session_id = request.state.session_id

    new_parcel = Parcel(**parcel_data.model_dump(), session_id=session_id)

    db.add(new_parcel)
    await db.commit()

    return {"id": new_parcel.id}


@router.get("", response_model=list[ParcelResponse])
async def get_my_parcels(
    request: Request,
    db: AsyncSession = Depends(get_async_session),
    limit: int = 10,
    offset: int = 0,
    type_id: Optional[int] = None,
    is_calculated: Optional[bool] = None,
):
    query = (
        select(Parcel)
        .options(joinedload(Parcel.type))
        .where(Parcel.session_id == request.state.session_id)
    )

    if type_id is not None:
        query = query.where(Parcel.type_id == type_id)

    if is_calculated is not None:
        if is_calculated:
            query = query.where(Parcel.delivery_cost.is_not(None))
        else:
            query = query.where(Parcel.delivery_cost.is_(None))

    query = query.offset(offset).limit(limit)

    result = await db.execute(query)
    parcels = result.scalars().all()

    for parcel in parcels:
        parcel.type_name = parcel.type.name

    return parcels


@router.get("/{parcel_id}", response_model=ParcelResponse)
async def get_parcel_by_id(
    parcel_id: uuid.UUID,
    request: Request,
    db: AsyncSession = Depends(get_async_session),
):
    query = (
        select(Parcel).options(joinedload(Parcel.type)).where(Parcel.id == parcel_id)
    )
    result = await db.execute(query)
    parcel = result.scalars().first()

    if not parcel or parcel.session_id != request.state.session_id:
        raise HTTPException(status_code=404, detail="Посылка не найдена")

    parcel.type_name = parcel.type.name
    return parcel


@router.post("/calculate-now")
def trigger_delivery_calculation():
    calculate_delivery_task.delay()
    return {
        "status": "success",
        "message": "Расчёт стоимости доставки успешно запущен в фоновом режиме",
    }
