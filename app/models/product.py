from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, Integer, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.database import Base

if TYPE_CHECKING:
    from .inventory_batch import InventoryBatch


class Product(Base):
    __tablename__ = "products"
    __table_args__ = (
        CheckConstraint("price >= 0", name="ck_products_price_nonnegative"),
        CheckConstraint(
            "shelf_life_days > 0",
            name="ck_products_shelf_life_positive",
        ),
    )

    # PostgreSQL generates this ID automatically.
    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    name: Mapped[str] = mapped_column(String(200), nullable=False)
    sku: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
    price: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    shelf_life_days: Mapped[int] = mapped_column(Integer, nullable=False)

    # One product can have multiple inventory batches.
    inventory_batches: Mapped[list[InventoryBatch]] = relationship(
        back_populates="product"
    )