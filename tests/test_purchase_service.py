from datetime import date, timedelta
from decimal import Decimal

from tests.test_support import ServiceTestCase

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.inventory_batch import InventoryBatch
from app.models.order import Order, OrderItem
from app.models.wallet import Wallet
from app.models.wallet_transaction import WalletTransaction
from app.services import purchase_service, wallet_service


class PurchaseServiceTests(ServiceTestCase):
    def setUp(self):
        super().setUp()
        self.user_id, self.wallet_id = self.create_user_with_wallet(
            balance=Decimal("100.00")
        )
        self.product = self.create_product(
            name="Purchase Product",
            sku="BUY-001",
            price=Decimal("10.00"),
            shelf_life_days=30,
        )

    def test_purchase_deducts_wallet_stock_and_records_order(self):
        batch_id = self.create_batch(self.product.id, quantity_received=2)

        order_id, total, new_balance = purchase_service.purchase_product(
            self.user_id,
            self.product.id,
            2,
        )

        self.assertEqual(total, Decimal("20.00"))
        self.assertEqual(new_balance, Decimal("80.00"))
        with Session(self.engine) as session:
            order = session.get(Order, order_id)
            item = session.scalar(
                select(OrderItem).where(OrderItem.order_id == order_id)
            )
            wallet = session.get(Wallet, self.wallet_id)
            transaction = session.scalar(
                select(WalletTransaction).where(
                    WalletTransaction.wallet_id == self.wallet_id
                )
            )

            self.assertEqual(order.total_amount, Decimal("20.00"))
            self.assertEqual(item.quantity, 2)
            self.assertEqual(item.inventory_batch_id, None)
            self.assertEqual(wallet.balance, Decimal("80.00"))
            self.assertEqual(transaction.transaction_type, "purchase")
            self.assertEqual(transaction.amount, Decimal("20.00"))
            self.assertIsNone(session.get(InventoryBatch, batch_id))

    def test_purchase_allocates_earliest_expiry_first(self):
        today = date.today()
        first_batch_id = self.create_batch(
            self.product.id,
            quantity_received=2,
            stock_in_date=today,
            expiry_date=today + timedelta(days=5),
        )
        second_batch_id = self.create_batch(
            self.product.id,
            quantity_received=5,
            stock_in_date=today,
            expiry_date=today + timedelta(days=10),
        )

        order_id, _, _ = purchase_service.purchase_product(
            self.user_id,
            self.product.id,
            3,
        )

        with Session(self.engine) as session:
            items = session.scalars(
                select(OrderItem)
                .where(OrderItem.order_id == order_id)
                .order_by(OrderItem.id)
            ).all()
            later_batch = session.get(InventoryBatch, second_batch_id)

            self.assertEqual([item.quantity for item in items], [2, 1])
            self.assertIsNone(items[0].inventory_batch_id)
            self.assertEqual(items[1].inventory_batch_id, second_batch_id)
            self.assertIsNone(session.get(InventoryBatch, first_batch_id))
            self.assertEqual(later_batch.quantity_remaining, 4)

    def test_future_dated_batch_cannot_be_purchased(self):
        future_date = date.today() + timedelta(days=5)
        self.create_batch(
            self.product.id,
            quantity_received=5,
            stock_in_date=future_date,
            expiry_date=future_date + timedelta(days=30),
        )

        with self.assertRaisesRegex(ValueError, "Not enough unexpired stock"):
            purchase_service.purchase_product(self.user_id, self.product.id, 1)

        self.assertEqual(
            wallet_service.get_wallet_balance(self.user_id),
            Decimal("100.00"),
        )

    def test_expired_batch_cannot_be_purchased(self):
        today = date.today()
        self.create_batch(
            self.product.id,
            quantity_received=5,
            stock_in_date=today - timedelta(days=40),
            expiry_date=today - timedelta(days=10),
        )

        with self.assertRaisesRegex(ValueError, "Not enough unexpired stock"):
            purchase_service.purchase_product(self.user_id, self.product.id, 1)

    def test_insufficient_stock_or_wallet_leaves_data_unchanged(self):
        batch_id = self.create_batch(self.product.id, quantity_received=1)

        with self.assertRaisesRegex(ValueError, "Not enough unexpired stock"):
            purchase_service.purchase_product(self.user_id, self.product.id, 2)

        with Session(self.engine) as session:
            batch = session.get(InventoryBatch, batch_id)
            self.assertEqual(batch.quantity_remaining, 1)

        with Session(self.engine) as session:
            wallet = session.get(Wallet, self.wallet_id)
            wallet.balance = Decimal("5.00")
            session.commit()

        with self.assertRaisesRegex(ValueError, "Insufficient wallet balance"):
            purchase_service.purchase_product(self.user_id, self.product.id, 1)

        with Session(self.engine) as session:
            self.assertEqual(session.get(InventoryBatch, batch_id).quantity_remaining, 1)
            self.assertEqual(session.get(Wallet, self.wallet_id).balance, Decimal("5.00"))
            self.assertEqual(session.scalar(select(func.count(Order.id))), 0)

    def test_purchase_rejects_nonpositive_or_non_integer_quantity(self):
        for quantity in (0, -1, 1.5, True):
            with self.subTest(quantity=quantity), self.assertRaises(ValueError):
                purchase_service.purchase_product(
                    self.user_id,
                    self.product.id,
                    quantity,
                )
