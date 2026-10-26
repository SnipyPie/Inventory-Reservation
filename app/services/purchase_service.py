from datetime import date

from sqlalchemy import select
from sqlalchemy.orm import Session
from decimal import Decimal
from app.models.inventory_batch import InventoryBatch
from app.models.product import Product
from app.models.wallet import Wallet
from app.database.database import engine
from app.models.order import Order, OrderItem
from app.models.wallet_transaction import WalletTransaction

def _get_available_batches_for_update(
    session: Session,
    product_id: int,
) -> list[InventoryBatch]:
    today = date.today()

    statement = (
        select(InventoryBatch)
        .where(
            InventoryBatch.product_id == product_id,
            InventoryBatch.quantity_remaining > 0,
            InventoryBatch.expiry_date >= today,
        )
        .order_by(
            InventoryBatch.expiry_date,
            InventoryBatch.stock_in_date,
            InventoryBatch.id,
        )
        .with_for_update()
    )

    return session.scalars(statement).all()

def _get_wallet_and_product_for_update(
    session: Session,
    user_id: int,
    product_id: int,
) -> tuple[Wallet, Product]:
    wallet = session.scalar(
        select(Wallet)
        .where(Wallet.user_id == user_id)
        .with_for_update()
    )
    if wallet is None:
        raise ValueError("No wallet was found for this user.")

    product = session.scalar(
        select(Product)
        .where(Product.id == product_id)
        .with_for_update()
    )
    if product is None:
        raise ValueError("Product not found.")

    return wallet, product

def _allocate_batch_quantities(
    batches: list[InventoryBatch],
    requested_quantity: int,
) -> list[tuple[InventoryBatch, int]]:
    if requested_quantity <= 0:
        raise ValueError("Quantity must be greater than zero.")

    remaining_to_allocate = requested_quantity
    allocations = []

    for batch in batches:
        if remaining_to_allocate == 0:
            break

        quantity_from_batch = min(
            batch.quantity_remaining,
            remaining_to_allocate,
        )

        if quantity_from_batch > 0:
            allocations.append((batch, quantity_from_batch))
            remaining_to_allocate -= quantity_from_batch

    if remaining_to_allocate > 0:
        already_allocated = requested_quantity - remaining_to_allocate
        raise ValueError(
            f"Not enough unexpired stock. Only {already_allocated} "
            "units are available."
        )

    return allocations

def _calculate_purchase_total(
    product: Product,
    wallet: Wallet,
    quantity: int,
) -> Decimal:
    total = product.price * quantity

    if total > wallet.balance:
        raise ValueError(
            f"Insufficient wallet balance. "
            f"Cost: {total:.2f}; balance: {wallet.balance:.2f}."
        )

    return total

def purchase_product(
user_id: int,
product_id: int,
quantity: int,):
    if not isinstance(quantity, int) or isinstance(quantity, bool) or quantity <= 0:
        raise ValueError("Quantity must be a positive whole number.")

    with Session(engine) as session:
        wallet, product = _get_wallet_and_product_for_update(
            session,
            user_id,
            product_id,
        )

        batches = _get_available_batches_for_update(session, product_id)
        allocations = _allocate_batch_quantities(batches, quantity)
        total = _calculate_purchase_total(product, wallet, quantity)

        order = Order(user_id=user_id, total_amount=total)
        session.add(order)
        session.flush()

        for batch, quantity_from_batch in allocations:
            batch.quantity_remaining -= quantity_from_batch

            order_item = OrderItem(
                order_id=order.id,
                product_id=product_id,
                inventory_batch_id=batch.id,
                quantity=quantity_from_batch,
                unit_price=product.price,
            )
            session.add(order_item)

        wallet.balance -= total

        if total > 0:
            transaction = WalletTransaction(
                wallet_id=wallet.id,
                transaction_type="purchase",
                amount=total,
            )
            session.add(transaction)

        session.commit()
        session.refresh(wallet)

        return order.id, total, wallet.balance