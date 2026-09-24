import uuid
from decimal import Decimal
from typing import TYPE_CHECKING, Optional

from sqlalchemy import ForeignKey, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database import Base

if TYPE_CHECKING:
    from src.models.parcel_type import ParcelType
    
class Parcel(Base):
    __tablename__ = "parcels"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)

    name: Mapped[str] = mapped_column(String(255), nullable=False)

    weight: Mapped[float] = mapped_column(nullable=False)

    content_value: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)

    delivery_cost: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(10, 2), nullable=True, default=None
    )

    session_id: Mapped[uuid.UUID] = mapped_column(nullable=False)

    type_id: Mapped[int] = mapped_column(ForeignKey("parcel_types.id"), nullable=False)

    type: Mapped["ParcelType"] = relationship()
