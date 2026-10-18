from app.models.product import Product
from sqlalchemy.orm import Session
from app.database.database import engine
from sqlalchemy import select, func


def create_product(product_id: int, name: str, price: float, quantity: int, sku: str):
    name = name.strip()
    sku = sku.strip()
    if not name:
        raise ValueError("Product name cannot be empty.")
    if not price or price <0 :
        raise ValueError("Price should be positive value")
    if quantity < 0:
        raise ValueError("Quantity cannot be negative.")
    
    product = Product(
        id=product_id,
        name=name,
        price=price,
        quantity=quantity,
        sku=sku,
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

def delete_product(product_id: int):
    with Session(engine) as session:
        product = session.get(Product, product_id)

        if product is None:
            return False

        session.delete(product)
        session.commit()
        return True

def update_product(product_id: int, updates: dict):
    allowed_fields = {"name", "price", "quantity", "sku"}

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