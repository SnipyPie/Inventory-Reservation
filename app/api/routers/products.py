from fastapi import APIRouter, HTTPException, status

from app.api.schemas.products import ProductResponse, ProductCreate, ProductUpdate, MessageResponse
from app.services import product_service

router = APIRouter(prefix="/products", tags=["products"])


@router.get("/{product_id}", response_model=ProductResponse)
def get_product_endpoint(product_id: int):
    product = product_service.get_product(product_id)

    if product is None:
        raise HTTPException(status_code=404, detail="Product not found.")

    return product

@router.get("/", response_model=list[ProductResponse])
def get_all_products():
    products = product_service.get_all_products()
    if products is None:
        raise HTTPException(status_code=404, detail="Product not found.")
    return products

@router.get("",response_model=list[ProductResponse])
def get_products(name: str | None= None):
    products = product_service.get_products_by_name(name)

    if products is None:
        raise HTTPException(status_code=404, detail="Product not found.")
    return products

@router.get("/by-sku/{sku}", response_model=ProductResponse)
def get_product_by_sku_endpoint(sku: str):
    product = product_service.get_product_by_sku(sku)

    if product is None:
        raise HTTPException(status_code=404, detail="Product not found.")

    return product

@router.post("",response_model=ProductResponse, status_code=status.HTTP_201_CREATED,)
def create_product_endpoint(data: ProductCreate):
    return product_service.create_product(
        name=data.name,
        sku=data.sku,
        price=data.price,
        shelf_life_days=data.shelf_life_days,
    )

@router.patch("/{product_id}")
def update_product(product_id: int, product_data: ProductUpdate):
    updates=product_data.model_dump(exclude_unset=True)
    products=product_service.update_product(product_id,updates)
    if products is None:
        raise HTTPException(status_code=404, detail="Product not found.")
    return products

@router.delete("/{product_id}",response_model=MessageResponse)
def delete_product_endpoint(product_id: int):
    result = product_service.delete_product(product_id)

    if result == "not_found":
        raise HTTPException(
            status_code=404,
            detail="Product not found.",
        )

    if result == "has_orders":
        raise HTTPException(
            status_code=409,
            detail="This product has past orders and cannot be deleted.",
        )

    if result == "has_batches":
        raise HTTPException(
            status_code=409,
            detail="Delete this product's inventory batches before deleting it.",
        )

    return {"message": "Product deleted successfully."}