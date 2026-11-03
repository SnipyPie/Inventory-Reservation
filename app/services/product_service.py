from decimal import Decimal
from app.models.product import Product
from app.models.order import OrderItem
from sqlalchemy.orm import Session
from app.database.database import engine
from sqlalchemy import select, func
from sqlalchemy.exc import IntegrityError


def _is_duplicate_sku_error(error: IntegrityError) -> bool:
    constraint_name = getattr(
        getattr(error.orig, "diag", None),
        "constraint_name",
        None,
    )
    sqlite_message = str(error.orig).lower()
    return (
        constraint_name == "products_sku_key"
        or "unique constraint failed: products.sku" in sqlite_message
    )


def _validate_price(price: Decimal) -> None:
    if not isinstance(price, Decimal) or not price.is_finite():
        raise ValueError("Price must be a valid decimal number.")

    if price < 0:
        raise ValueError("Price cannot be negative.")

    if price > Decimal("99999999.99"):
        raise ValueError("Price is too large.")

    if price != price.quantize(Decimal("0.01")):
        raise ValueError("Price can have at most two decimal places.")


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

    _validate_price(price)

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
        try:
            session.commit()
        except IntegrityError as error:
            session.rollback()
            if _is_duplicate_sku_error(error):
                raise ValueError("That SKU already exists.") from error
            raise
        session.refresh(product)

    return product

def get_product(product_id: int):
    with Session(engine) as session:
        return session.get(Product, product_id)
    
def get_products_by_name(name: str):
    name = name.strip()

    if not name:
        return []

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

        past_order_item = session.scalar(
            select(OrderItem.id)
            .where(OrderItem.product_id == product_id)
            .limit(1)
        )

        if past_order_item is not None:
            return "has_orders"

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
        _validate_price(updates["price"])

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

        try:
            session.commit()
        except IntegrityError as error:
            session.rollback()
            if _is_duplicate_sku_error(error):
                raise ValueError("That SKU already exists.") from error
            raise
        session.refresh(product)
        return product
