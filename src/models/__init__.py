from src.database import Base
from src.models.parcel import Parcel
from src.models.parcel_type import ParcelType

# Указываем, какие классы видны при импорте папки models
__all__ = ["Base", "Parcel", "ParcelType"]
