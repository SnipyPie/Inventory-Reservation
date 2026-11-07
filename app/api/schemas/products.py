from decimal import Decimal

from pydantic import BaseModel, ConfigDict


class ProductResponse(BaseModel):
    id: int
    name: str
    sku: str
    price: Decimal
    shelf_life_days: int

    # Allows Pydantic to read these fields from a SQLAlchemy Product object.
    model_config = ConfigDict(from_attributes=True)