from datetime import date, timedelta

from sqlalchemy.orm import Session

from app.database.database import engine
from app.models.inventory_batch import InventoryBatch
from app.models.product import Product


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