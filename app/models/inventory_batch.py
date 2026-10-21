from __future__ import annotations

from datetime import date

from sqlalchemy import CheckConstraint, Date, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.database import Base
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .product import Product
    
class InventoryBatch(Base):
    __tablename__ = "inventory_batches"
    __table_args__ = (
        CheckConstraint("quantity >= 0", name="ck_batches_quantity_nonnegative"),
        CheckConstraint(
            "expiry_date >= stock_in_date",
            name="ck_batches_expiry_after_stock_in",
        ),
    )

    # The database generates each batch ID.
    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    product_id: Mapped[int] = mapped_column(
        ForeignKey("products.id", ondelete="RESTRICT"),
        nullable=False,
    )
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    stock_in_date: Mapped[date] = mapped_column(
        Date,
        nullable=False,
        default=date.today,
    )
    expiry_date: Mapped[date] = mapped_column(Date, nullable=False)

    product: Mapped[Product] = relationship(
        back_populates="inventory_batches"
    )