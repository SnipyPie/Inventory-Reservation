from datetime import date, timedelta

from tests.test_support import ServiceTestCase

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.inventory_batch import InventoryBatch
from app.services import inventory_service


class InventoryServiceTests(ServiceTestCase):
    def test_add_batch_sets_expiry_from_product_shelf_life(self):
        product = self.create_product(shelf_life_days=14)
        stock_date = date.today()

        batch = inventory_service.add_inventory_batch(
            product.id,
            5,
            stock_date,
        )

        self.assertEqual(batch.quantity_received, 5)
        self.assertEqual(batch.quantity_remaining, 5)
        self.assertEqual(batch.expiry_date, stock_date + timedelta(days=14))

    def test_add_batch_rejects_nonpositive_quantity_and_missing_product(self):
        product = self.create_product()

        with self.assertRaisesRegex(ValueError, "greater than zero"):
            inventory_service.add_inventory_batch(product.id, 0)

        self.assertIsNone(inventory_service.add_inventory_batch(9999, 1))

    def test_future_batch_is_not_counted_as_available(self):
        product = self.create_product()
        future_date = date.today() + timedelta(days=5)
        inventory_service.add_inventory_batch(product.id, 5, future_date)

        row = inventory_service.get_inventory_summary_by_name("Test Product")[0]

        self.assertEqual(row["available_quantity"], 0)
        self.assertEqual(row["expired_quantity"], 0)
        self.assertEqual(row["total_quantity"], 5)

    def test_summary_counts_expired_quantity_and_includes_empty_products(self):
        expired_product = self.create_product(
            name="Old Product", sku="OLD-001", shelf_life_days=5
        )
        self.create_batch(
            expired_product.id,
            quantity_received=5,
            quantity_remaining=3,
            stock_in_date=date.today() - timedelta(days=10),
            expiry_date=date.today() - timedelta(days=5),
        )
        self.create_product(name="Empty Product", sku="EMPTY-001")

        rows = inventory_service.get_inventory_summary_by_name("Product")
        by_name = {row["name"]: row for row in rows}

        self.assertEqual(by_name["Old Product"]["available_quantity"], 0)
        self.assertEqual(by_name["Old Product"]["expired_quantity"], 3)
        self.assertEqual(by_name["Empty Product"]["batch_count"], 0)
        self.assertEqual(by_name["Empty Product"]["total_quantity"], 0)

    def test_blank_inventory_search_raises_value_error(self):
        with self.assertRaisesRegex(ValueError, "Search name cannot be empty"):
            inventory_service.get_inventory_summary_by_name("   ")

    def test_batch_search_is_case_insensitive_and_blank_search_is_rejected(self):
        product = self.create_product(name="Apples", sku="APL-001")
        batch_id = self.create_batch(product.id, 4)

        rows = inventory_service.get_inventory_batches_by_name(" APPLE ")

        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0][0].id, batch_id)
        self.assertEqual(rows[0][1], "Apples")

        with self.assertRaisesRegex(ValueError, "Search name cannot be empty"):
            inventory_service.get_inventory_batches_by_name(" ")

    def test_update_rejects_remaining_above_received(self):
        product = self.create_product()
        batch_id = self.create_batch(product.id, quantity_received=5)

        with self.assertRaisesRegex(ValueError, "cannot exceed"):
            inventory_service.update_inventory_batch(batch_id, quantity=99)

        with Session(self.engine) as session:
            batch = session.get(InventoryBatch, batch_id)
            self.assertEqual(batch.quantity_remaining, 5)

    def test_database_constraint_rejects_remaining_above_received(self):
        product = self.create_product()

        with self.assertRaises(IntegrityError):
            with Session(self.engine) as session:
                session.add(
                    InventoryBatch(
                        product_id=product.id,
                        quantity_received=5,
                        quantity_remaining=6,
                        stock_in_date=date.today(),
                        expiry_date=date.today() + timedelta(days=30),
                    )
                )
                session.commit()

    def test_update_quantity_and_stock_date_recalculate_expiry(self):
        product = self.create_product(shelf_life_days=14)
        batch_id = self.create_batch(product.id, quantity_received=5)
        new_stock_date = date.today() - timedelta(days=2)

        updated = inventory_service.update_inventory_batch(
            batch_id,
            quantity=4,
            stock_in_date=new_stock_date,
        )

        self.assertEqual(updated.quantity_remaining, 4)
        self.assertEqual(updated.expiry_date, new_stock_date + timedelta(days=14))

    def test_setting_remaining_to_zero_deletes_batch(self):
        product = self.create_product()
        batch_id = self.create_batch(product.id, quantity_received=1)

        result = inventory_service.update_inventory_batch(batch_id, quantity=0)

        self.assertEqual(result, "deleted")
        self.assertIsNone(inventory_service.update_inventory_batch(batch_id))

    def test_delete_batch_reports_missing_id(self):
        self.assertFalse(inventory_service.delete_inventory_batch(9999))
