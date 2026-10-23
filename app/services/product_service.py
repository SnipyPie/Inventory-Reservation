from decimal import Decimal
from app.models.product import Product
from sqlalchemy.orm import Session
from app.database.database import engine
from sqlalchemy import select, func


def create_product(
    name: str,
    sku: str,
    price: Decimal,
    shelf_life_days: int,
):
    name = name.strip()
    sku = sku.strip()

    if not name:
        raise ValueError("Product name cannot be empty.")

    if not sku:
        raise ValueError("Product SKU cannot be empty.")

    if price < 0:
        raise ValueError("Price cannot be negative.")

    if shelf_life_days <= 0:
        raise ValueError("Shelf life must be greater than zero.")

    product = Product(
        name=name,
        sku=sku,
        price=price,
        shelf_life_days=shelf_life_days,
    )

    with Session(engine) as session:
        session.add(product)
        session.commit()
        session.refresh(product)

    return product

def get_product(product_id: int):
    with Session(engine) as session:
        return session.get(Product, product_id)
    
def get_products_by_name(name: str):
    with Session(engine) as session:
        statement = (
            select(Product)
            .where(func.lower(Product.name) == name.lower())
            .order_by(Product.id)
        )
        return session.scalars(statement).all()


def get_all_products():
    with Session(engine) as session:
        statement = select(Product).order_by(Product.id)
        return session.scalars(statement).all()

def delete_product(product_id: int) -> str:
    with Session(engine) as session:
        product = session.get(Product, product_id)

        if product is None:
            return "not_found"

        if product.inventory_batches:
            return "has_batches"

        session.delete(product)
        session.commit()
        return "deleted"

def update_product(product_id: int, updates: dict):
    allowed_fields = {"name", "price", "sku", "shelf_life_days"}
    updates = {
        key: value
        for key, value in updates.items()
        if key in allowed_fields
    }

    if "name" in updates and isinstance(updates["name"], str):
        updates["name"] = updates["name"].strip()
        if not updates["name"]:
            raise ValueError("Product name cannot be empty.")

    if "sku" in updates and isinstance(updates["sku"], str):
        updates["sku"] = updates["sku"].strip()
        if not updates["sku"]:
            raise ValueError("Product sku cannot be empty.")
    
    if "price" in updates:
        if not isinstance(updates["price"], (int, float)):
            raise ValueError("Price must be numeric")
        if updates["price"] < 0:
            raise ValueError("Price cannot be negative.")

    if "shelf_life_days" in updates:
        if not isinstance(updates["shelf_life_days"], int):
            raise ValueError("Shelf life must be a whole number.")
        if updates["shelf_life_days"] <= 0:
            raise ValueError("Shelf life must be greater than zero.")
        
    with Session(engine) as session:
        product = session.get(Product, product_id)

        if product is None:
            return None

        for field, value in updates.items():
            if field in allowed_fields:
                setattr(product, field, value)

        session.commit()
        session.refresh(product)
        return product