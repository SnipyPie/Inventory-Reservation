from datetime import date

from pydantic import BaseModel, ConfigDict, Field


class InventoryResponse(BaseModel):
    product_id: int
    name: str
    sku: str
    available_quantity: int
    expired_quantity: int
    total_quantity: int
    batch_count: int


class InventoryBatchResponse(BaseModel):
    id: int
    product_id: int
    product_name: str
    sku: str
    quantity_received: int
    quantity_remaining: int
    stock_in_date: date
    expiry_date: date


class InventoryBatchCreate(BaseModel):
    product_id: int
    quantity: int = Field(gt=0)
    stock_in_date: date | None = None


class InventoryBatchCreatedResponse(BaseModel):
    id: int
    product_id: int
    quantity_received: int
    quantity_remaining: int
    stock_in_date: date
    expiry_date: date

    model_config = ConfigDict(from_attributes=True)

class InventoryBatchUpdate(BaseModel):
    quantity: int | None=Field(default=None,ge=0)
    stock_in_date: date| None=None

class InventoryBatchDelete(BaseModel):
    message: str