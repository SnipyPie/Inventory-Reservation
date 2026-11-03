"""Shared isolated SQLite setup for service and action tests."""

import os
import unittest
from datetime import date, timedelta
from decimal import Decimal
from unittest.mock import patch

from sqlalchemy import create_engine, event
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

# database.py needs a value while it creates its normal engine. Service tests
# replace each service's engine with SQLite before making any database calls.
os.environ.setdefault("DB_PASSWORD", "tests-do-not-connect-to-the-project-db")

import app.models  # noqa: F401  # Register every model with Base.metadata.
from app.database.database import Base
from app.models.inventory_batch import InventoryBatch
from app.models.user import User
from app.models.wallet import Wallet
from app.services import (
    inventory_service,
    order_service,
    product_service,
    purchase_service,
    user_service,
    wallet_service,
)


SERVICE_MODULES = (
    inventory_service,
    order_service,
    product_service,
    purchase_service,
    user_service,
    wallet_service,
)


class ServiceTestCase(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine(
            "sqlite+pysqlite:///:memory:",
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
        )

        @event.listens_for(self.engine, "connect")
        def enable_sqlite_foreign_keys(connection, _record):
            cursor = connection.cursor()
            cursor.execute("PRAGMA foreign_keys=ON")
            cursor.close()

        self.addCleanup(self.engine.dispose)

        for service_module in SERVICE_MODULES:
            engine_patch = patch.object(service_module, "engine", self.engine)
            engine_patch.start()
            self.addCleanup(engine_patch.stop)

        Base.metadata.create_all(self.engine)

    def tearDown(self):
        Base.metadata.drop_all(self.engine)

    def create_product(
        self,
        name="Test Product",
        sku="TEST-001",
        price=Decimal("10.00"),
        shelf_life_days=30,
    ):
        return product_service.create_product(
            name=name,
            sku=sku,
            price=price,
            shelf_life_days=shelf_life_days,
        )

    def create_user_with_wallet(
        self,
        email="customer@example.com",
        balance=Decimal("0.00"),
    ):
        with Session(self.engine) as session:
            user = User(email=email, password_hash="test-hash")
            session.add(user)
            session.flush()

            wallet = Wallet(user_id=user.id, balance=balance)
            session.add(wallet)
            session.commit()
            return user.id, wallet.id

    def create_batch(
        self,
        product_id,
        quantity_received,
        quantity_remaining=None,
        stock_in_date=None,
        expiry_date=None,
    ):
        stock_in_date = stock_in_date or date.today()
        quantity_remaining = (
            quantity_received
            if quantity_remaining is None
            else quantity_remaining
        )
        expiry_date = expiry_date or stock_in_date + timedelta(days=30)

        with Session(self.engine) as session:
            batch = InventoryBatch(
                product_id=product_id,
                quantity_received=quantity_received,
                quantity_remaining=quantity_remaining,
                stock_in_date=stock_in_date,
                expiry_date=expiry_date,
            )
            session.add(batch)
            session.commit()
            return batch.id
