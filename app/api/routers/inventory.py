from fastapi import APIRouter, HTTPException

from app.api.schemas.inventory import InventoryResponse
from app.services import inventory_service

router = APIRouter(prefix="/inventory", tags=["inventory"])


@router.get("/{prod_name}", response_model=list[InventoryResponse])
def get_inventory_by_name(prod_name: str):
    results = inventory_service.get_inventory_summary_by_name(prod_name)

    if not results:
        raise HTTPException(status_code=404, detail="Product not found.")

    return results