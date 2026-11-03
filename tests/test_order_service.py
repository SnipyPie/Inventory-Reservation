from decimal import Decimal

from tests.test_support import ServiceTestCase

from sqlalchemy.orm import Session

from app.models.order import Order, OrderItem
from app.services import order_service


class OrderServiceTests(ServiceTestCase):
    def test_history_returns_only_the_requested_users_orders_with_item_details(self):
        first_user_id, _ = self.create_user_with_wallet(email="first@example.com")
        second_user_id, _ = self.create_user_with_wallet(email="second@example.com")
        product = self.create_product(name="Apple", sku="APL-001")

        with Session(self.engine) as session:
            first_order = Order(
                user_id=first_user_id,
                total_amount=Decimal("20.00"),
            )
            second_order = Order(
                user_id=second_user_id,
                total_amount=Decimal("10.00"),
            )
            session.add_all([first_order, second_order])
            session.flush()
            first_order_id = first_order.id
            session.add_all(
                [
                    OrderItem(
                        order_id=first_order.id,
                        product_id=product.id,
                        inventory_batch_id=None,
                        quantity=2,
                        unit_price=Decimal("10.00"),
                    ),
                    OrderItem(
                        order_id=second_order.id,
                        product_id=product.id,
                        inventory_batch_id=None,
                        quantity=1,
                        unit_price=Decimal("10.00"),
                    ),
                ]
            )
            session.commit()

        rows = order_service.get_customer_order_history(first_user_id)

        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0].order_id, first_order_id)
        self.assertEqual(rows[0].product_name, "Apple")
        self.assertEqual(rows[0].sku, "APL-001")
        self.assertEqual(rows[0].quantity, 2)
        self.assertEqual(rows[0].unit_price, Decimal("10.00"))

    def test_customer_without_orders_gets_empty_list(self):
        user_id, _ = self.create_user_with_wallet()
        self.assertEqual(order_service.get_customer_order_history(user_id), [])
