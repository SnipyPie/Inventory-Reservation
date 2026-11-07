from pydantic import BaseModel


class InventoryResponse(BaseModel):
    product_id: int
    name: str
    sku: str
    available_quantity: int
    expired_quantity: int
    total_quantity: int
    batch_count: int

