from app.models.product import Product
from sqlalchemy.orm import Session
from app.database.database import engine
from sqlalchemy import select, func

products=[]

def create_product(product_id, name, price, quantity, sku):
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
    
def get_products_by_name(name):
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