from datetime import date, timedelta

from sqlalchemy.orm import Session

from app.database.database import engine
from app.models.inventory_batch import InventoryBatch
from app.models.product import Product
from sqlalchemy import case, func, select

def add_inventory_batch(
    product_id: int,
    quantity: int,
    stock_in_date: date | None = None,
):
    if quantity <= 0:
        raise ValueError("Batch quantity must be greater than zero.")

    if stock_in_date is None:
        stock_in_date = date.today()

    with Session(engine) as session:
        product = session.get(Product, product_id)

        if product is None:
            return None

        expiry_date = stock_in_date + timedelta(
            days=product.shelf_life_days
        )

        batch = InventoryBatch(
            product_id=product.id,
            quantity=quantity,
            stock_in_date=stock_in_date,
            expiry_date=expiry_date,
        )

        product.quantity += quantity
        session.add(batch)
        session.commit()
        session.refresh(batch)

        return batch
def get_inventory_summary_by_name(name: str):
    search_name = name.strip()

    if not search_name:
        raise ValueError("Search name cannot be empty.")

    today = date.today()

    available_quantity = func.coalesce(
        func.sum(
            case(
                (InventoryBatch.expiry_date >= today, InventoryBatch.quantity),
                else_=0,
            )
        ),
        0,
    ).label("available_quantity")

    expired_quantity = func.coalesce(
        func.sum(
            case(
                (InventoryBatch.expiry_date < today, InventoryBatch.quantity),
                else_=0,
            )
        ),
        0,
    ).label("expired_quantity")

    total_quantity = func.coalesce(
        func.sum(InventoryBatch.quantity),
        0,
    ).label("total_quantity")
    batch_count = func.count(InventoryBatch.id).label("batch_count")
    statement = (
        select(
            Product.id.label("product_id"),
            Product.name,
            Product.sku,
            available_quantity,
            expired_quantity,
            total_quantity,
            batch_count,
        )
        .outerjoin(InventoryBatch, InventoryBatch.product_id == Product.id)
        .where(func.lower(Product.name).contains(search_name.lower()))
        .group_by(Product.id, Product.name, Product.sku)
        .order_by(Product.name, Product.sku)
    )

    with Session(engine) as session:
        return session.execute(statement).mappings().all()