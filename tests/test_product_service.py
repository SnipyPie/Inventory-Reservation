from decimal import Decimal
from datetime import date

from tests.test_support import ServiceTestCase

from sqlalchemy.orm import Session

from app.models.inventory_batch import InventoryBatch
from app.models.order import Order, OrderItem
from app.services import product_service


class ProductServiceTests(ServiceTestCase):
    def test_create_get_list_and_case_insensitive_name_search(self):
        product = self.create_product(name="Apple", sku="APL-001")
        self.create_product(name="Pear", sku="PEAR-001")

        self.assertEqual(product_service.get_product(product.id).sku, "APL-001")
        self.assertEqual(len(product_service.get_all_products()), 2)
        matches = product_service.get_products_by_name("aPpLe")
        self.assertEqual([item.id for item in matches], [product.id])
        self.assertEqual(product_service.get_products_by_name("  "), [])

    def test_create_rejects_duplicate_sku_with_friendly_error(self):
        self.create_product(sku="DUP-001")

        with self.assertRaisesRegex(ValueError, "That SKU already exists"):
            self.create_product(name="Another Product", sku="DUP-001")

    def test_create_and_update_use_decimal_price_validation(self):
        product = self.create_product(price=Decimal("9.99"))

        updated = product_service.update_product(
            product.id,
            {"price": Decimal("12.50")},
        )

        self.assertEqual(updated.price, Decimal("12.50"))

        with self.assertRaisesRegex(ValueError, "valid decimal"):
            product_service.update_product(product.id, {"price": 12.50})

        with self.assertRaisesRegex(ValueError, "at most two decimal places"):
            product_service.create_product(
                name="Precise Product",
                sku="PRECISE-001",
                price=Decimal("12.501"),
                shelf_life_days=10,
            )

    def test_update_rejects_duplicate_sku(self):
        self.create_product(name="First", sku="FIRST-001")
        second = self.create_product(name="Second", sku="SECOND-001")

        with self.assertRaisesRegex(ValueError, "That SKU already exists"):
            product_service.update_product(second.id, {"sku": "FIRST-001"})

    def test_delete_product_with_past_order_returns_has_orders(self):
        product = self.create_product()
        user_id, _wallet_id = self.create_user_with_wallet()

        with Session(self.engine) as session:
            order = Order(user_id=user_id, total_amount=Decimal("10.00"))
            session.add(order)
            session.flush()
            session.add(
                OrderItem(
                    order_id=order.id,
                    product_id=product.id,
                    inventory_batch_id=None,
                    quantity=1,
                    unit_price=Decimal("10.00"),
                )
            )
            session.commit()

        self.assertEqual(product_service.delete_product(product.id), "has_orders")
        self.assertIsNotNone(product_service.get_product(product.id))

    def test_delete_product_with_batches_is_blocked(self):
        product = self.create_product()
        with Session(self.engine) as session:
            session.add(
                InventoryBatch(
                    product_id=product.id,
                    quantity_received=2,
                    quantity_remaining=2,
                    stock_in_date=date.today(),
                    expiry_date=date.today(),
                )
            )
            session.commit()

        self.assertEqual(product_service.delete_product(product.id), "has_batches")

    def test_delete_product_without_dependencies_succeeds(self):
        product = self.create_product()

        self.assertEqual(product_service.delete_product(product.id), "deleted")
        self.assertIsNone(product_service.get_product(product.id))
