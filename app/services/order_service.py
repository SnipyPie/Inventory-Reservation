from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database.database import engine
from app.models.order import Order, OrderItem
from app.models.product import Product


def get_customer_order_history(user_id: int):
    with Session(engine) as session:
        statement = (
            select(
                Order.id.label("order_id"),
                Order.created_at,
                Order.total_amount,
                Product.name.label("product_name"),
                Product.sku,
                OrderItem.quantity,
                OrderItem.unit_price,
            )
            .join(OrderItem, OrderItem.order_id == Order.id)
            .join(Product, Product.id == OrderItem.product_id)
            .where(Order.user_id == user_id)
            .order_by(
                Order.created_at.desc(),
                Order.id.desc(),
                OrderItem.id,
            )
        )

        return session.execute(statement).all()