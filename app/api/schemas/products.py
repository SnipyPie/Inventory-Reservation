from decimal import Decimal
from pydantic import BaseModel, ConfigDict, Field


class ProductResponse(BaseModel):
    id: int
    name: str
    sku: str
    price: Decimal
    shelf_life_days: int

    # Allows Pydantic to read these fields from a SQLAlchemy Product object.
    model_config = ConfigDict(from_attributes=True)

class ProductCreate(BaseModel):
    name: str
    sku: str
    price: Decimal
    shelf_life_days: int

class ProductUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1,max_length=200)
    sku: str | None = Field(default=None,min_length=1,max_length=50)
    price: Decimal | None = Field(default=None,ge=0)
    shelf_life_days: int | None = Field(default=None,gt=0)

class MessageResponse(BaseModel):
    message: str