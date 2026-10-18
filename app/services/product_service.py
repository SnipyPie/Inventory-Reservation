from app.models.product import Product
from sqlalchemy.orm import Session
from app.database.database import engine

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

def get_product(name):
    for product in products:
        if product.name.lower()==name.lower():
            return product
    return None

matching_names=[]
def get_products_by_name(name):
    for product in products:
        if product.name.lower()==name.lower():
            matching_names.append(product)
    return matching_names

def get_all_products():
    return products

def delete_product(product_id: str):
    for product in products:
        if product.id==product_id:
            products.remove(product)
            return True
    return False

def update_product(product_id: str,updates: dict):
    for product in products:
        if product.id==product_id:
            if "name"in updates:
                product.name=updates["name"]
            if "price" in updates:
                product.price=updates["price"]
            if "quantity" in updates:
                product.quantity=updates["quantity"]
            if "sku" in updates:
                product.sku=updates["sku"]
            return product
        return None
