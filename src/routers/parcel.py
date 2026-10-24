import uuid
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from fastapi.responses import Response
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from src.database import get_async_session
from src.models import Parcel, ParcelType
from src.schemas.parcel import ParcelCreate, ParcelPage, ParcelResponse
from src.worker import calculate_delivery_task

router = APIRouter(prefix="/parcels", tags=["Parcels"])


async def _get_owned_parcel(
    parcel_id: uuid.UUID, request: Request, db: AsyncSession
) -> Parcel:
    """Возвращает посылку только если она принадлежит текущей сессии."""
    query = (
        select(Parcel).options(joinedload(Parcel.type)).where(Parcel.id == parcel_id)
    )
    result = await db.execute(query)
    parcel = result.scalars().first()

    if parcel is None or parcel.session_id != request.state.session_id:
        raise HTTPException(status_code=404, detail="Посылка не найдена")

    parcel.type_name = parcel.type.name if parcel.type else None
    return parcel


# Пользователь дает данные о посылке, мы валидируем, присваиваем session_id посылке
# и добавляем данные в бд
@router.post("", response_model=ParcelResponse, status_code=status.HTTP_201_CREATED)
async def create_parcel(
    parcel_data: ParcelCreate,
    request: Request,
    db: AsyncSession = Depends(get_async_session),
):
    type_check = await db.execute(
        select(ParcelType).where(ParcelType.id == parcel_data.type_id)
    )
    parcel_type = type_check.scalars().first()
    if parcel_type is None:
        raise HTTPException(
            status_code=400, detail="Указанный тип посылки не существует"
        )

    new_parcel = Parcel(
        **parcel_data.model_dump(),
        session_id=request.state.session_id,
    )

    db.add(new_parcel)
    await db.commit()

    parcel = await _get_owned_parcel(new_parcel.id, request, db)
    return parcel


# Эндпоинт позволяющий пользователю посмотреть его посылки, используя фильтры
@router.get("", response_model=ParcelPage)
async def get_my_parcels(
    request: Request,
    db: AsyncSession = Depends(get_async_session),
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
    type_id: Optional[int] = None,
    is_calculated: Optional[bool] = None,
):
    filters = [Parcel.session_id == request.state.session_id]

    if type_id is not None:
        filters.append(Parcel.type_id == type_id)

    if is_calculated is True:
        filters.append(Parcel.delivery_cost.is_not(None))
    elif is_calculated is False:
        filters.append(Parcel.delivery_cost.is_(None))

    total = await db.scalar(select(func.count()).select_from(Parcel).where(*filters))

    query = (
        select(Parcel)
        .options(joinedload(Parcel.type))
        .where(*filters)
        .order_by(Parcel.created_at.desc(), Parcel.id.desc())
        .offset(offset)
        .limit(limit)
    )

    result = await db.execute(query)
    parcels = list(result.scalars().all())

    for parcel in parcels:
        parcel.type_name = parcel.type.name if parcel.type else None

    return ParcelPage(
        items=[ParcelResponse.model_validate(parcel) for parcel in parcels],
        total=total or 0,
        limit=limit,
        offset=offset,
    )


# Эндпоинт позволяющий пользователю найти свою посылку по айди, чужие не получится
@router.get("/{parcel_id}", response_model=ParcelResponse)
async def get_parcel_by_id(
    parcel_id: uuid.UUID,
    request: Request,
    db: AsyncSession = Depends(get_async_session),
):
    return await _get_owned_parcel(parcel_id, request, db)


# Удаление посылки пользователя
@router.delete("/{parcel_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_parcel(
    parcel_id: uuid.UUID,
    request: Request,
    db: AsyncSession = Depends(get_async_session),
):
    parcel = await _get_owned_parcel(parcel_id, request, db)

    await db.delete(parcel)
    await db.commit()

    return Response(status_code=status.HTTP_204_NO_CONTENT)


# Пересчет стоимости конкретной посылки: сбрасываем стоимость и ставим задачу в очередь
@router.post("/{parcel_id}/recalculate", status_code=status.HTTP_202_ACCEPTED)
async def recalculate_parcel(
    parcel_id: uuid.UUID,
    request: Request,
    db: AsyncSession = Depends(get_async_session),
):
    parcel = await _get_owned_parcel(parcel_id, request, db)

    parcel.delivery_cost = None
    await db.commit()

    calculate_delivery_task.delay()

    return {
        "status": "accepted",
        "message": "Пересчёт стоимости поставлен в очередь",
    }


# Запуск перерасчета стоимости доставки посылок в ручном режиме,
# для отладки и проверки работы
@router.post("/calculate-now")
def trigger_delivery_calculation():
    calculate_delivery_task.delay()
    return {
        "status": "success",
        "message": "Расчёт стоимости доставки успешно запущен в фоновом режиме",
    }
