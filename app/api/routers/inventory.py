from fastapi import APIRouter, HTTPException, status

from app.api.schemas.inventory import InventoryResponse, InventoryBatchCreatedResponse, InventoryBatchCreate, InventoryBatchResponse, InventoryBatchUpdate, InventoryBatchDelete
from app.services import inventory_service

router = APIRouter(prefix="/inventory", tags=["inventory"])


@router.get("/{prod_name}", response_model=list[InventoryResponse])
def get_inventory_by_name(prod_name: str):
    results = inventory_service.get_inventory_summary_by_name(prod_name)

    if not results:
        raise HTTPException(status_code=404, detail="Batch not found.")

    return results

@router.get("",response_model=list[InventoryResponse])
def get_all_inventory_summary():
    results = inventory_service.get_all_inventory_summary()
    if not results:
        raise HTTPException(status_code=404, detail="Batch not found.")
    return results

@router.get("/batches/{product_name}",response_model=list[InventoryBatchResponse])
def get_inventory_batches(product_name: str):
    results = inventory_service.get_inventory_batches_by_name(product_name)
    if not results:
            raise HTTPException(status_code=404, detail="Batch not found.")
    return [
        {
            "id": batch.id,
            "product_id": batch.product_id,
            "product_name": name,
            "sku": sku,
            "quantity_received": batch.quantity_received,
            "quantity_remaining": batch.quantity_remaining,
            "stock_in_date": batch.stock_in_date,
            "expiry_date": batch.expiry_date,
        }
        for batch, name, sku in results
    ]

@router.post("/batches",response_model=InventoryBatchCreatedResponse,status_code=status.HTTP_201_CREATED,)
def create_inventory_batch(data: InventoryBatchCreate):
    batch = inventory_service.add_inventory_batch(
        product_id=data.product_id,
        quantity=data.quantity,
        stock_in_date=data.stock_in_date,
    )

    if batch is None:
        raise HTTPException(status_code=404, detail="Batch not found.")

    return batch

@router.patch("/batches/{batch_id}",response_model=InventoryBatchCreatedResponse,status_code=200)
def update_inventory_batch(batch_id: int,data: InventoryBatchUpdate):
    try:
        updated_batch = inventory_service.update_inventory_batch(
        batch_id=batch_id,
        quantity=data.quantity,
        stock_in_date=data.stock_in_date,
    )
    except ValueError as error:
        raise HTTPException(status_code=422, detail=str(error)) from error

    if updated_batch is None:
        raise HTTPException(status_code=404, detail="Batch not found.")

    return updated_batch

@router.delete("/batches/{batch_id}",response_model=InventoryBatchDelete)
def inventory_batch_delete(batch_id: int):
    deleted = inventory_service.delete_inventory_batch(batch_id)
    if deleted== False:
        raise HTTPException(status_code=404, detail="Batch not found.")
    return {"message":"Inventory Batch Deleted successfully"}