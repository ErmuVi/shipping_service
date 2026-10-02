from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_async_session
from src.models import ParcelType
from src.schemas.parcel_type import ParcelTypeRead

router = APIRouter(prefix="/types", tags=["Types"])

#Эндпоинт позволяющий узнать какие типы посылок есть в сервисе
@router.get("", response_model=list[ParcelTypeRead])
async def read_types(db: AsyncSession = Depends(get_async_session)):
    query = select(ParcelType)
    result = await db.execute(query)
    types = result.scalars().all()
    return types
