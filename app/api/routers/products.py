from fastapi import APIRouter, HTTPException

from app.api.schemas.products import ProductResponse
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