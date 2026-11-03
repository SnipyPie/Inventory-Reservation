from contextlib import redirect_stdout
from decimal import Decimal
from io import StringIO
from types import SimpleNamespace
from unittest.mock import patch

from tests.test_support import ServiceTestCase

import actions


class ProductAndSummaryActionTests(ServiceTestCase):
    def test_get_product_retries_non_numeric_id(self):
        output = StringIO()
        with (
            patch("builtins.input", side_effect=["1", "abc", "7"]),
            patch.object(actions.product_service, "get_product", return_value=None) as get_product,
            redirect_stdout(output),
        ):
            actions.get_product_action()

        get_product.assert_called_once_with(7)
        self.assertIn("Enter a whole number.", output.getvalue())

    def test_update_product_retries_non_numeric_id(self):
        product = SimpleNamespace(
            id=7,
            name="Test Product",
            price=Decimal("10.00"),
            sku="TEST-001",
            shelf_life_days=30,
        )
        output = StringIO()
        with (
            patch("builtins.input", side_effect=["1", "abc", "7", "5"]),
            patch.object(actions.product_service, "get_product", return_value=product) as get_product,
            patch.object(actions, "display_product"),
            redirect_stdout(output),
        ):
            actions.update_product_action()

        get_product.assert_called_once_with(7)
        self.assertIn("Enter a whole number.", output.getvalue())

    def test_update_product_name_selection_retries_non_numeric_id(self):
        product = SimpleNamespace(
            id=7,
            name="Test Product",
            price=Decimal("10.00"),
            sku="TEST-001",
            shelf_life_days=30,
        )
        output = StringIO()
        with (
            patch(
                "builtins.input",
                side_effect=["2", "Test Product", "abc", "7", "5"],
            ),
            patch.object(
                actions.product_service,
                "get_products_by_name",
                return_value=[product],
            ),
            patch.object(
                actions.product_service,
                "get_product",
                return_value=product,
            ) as get_product,
            patch.object(actions, "display_product"),
            redirect_stdout(output),
        ):
            actions.update_product_action()

        get_product.assert_called_once_with(7)
        self.assertIn("Enter a whole number.", output.getvalue())

    def test_blank_inventory_summary_returns_friendly_message(self):
        output = StringIO()
        with (
            patch("builtins.input", return_value="   "),
            patch.object(
                actions,
                "get_inventory_summary_by_name",
                side_effect=ValueError("Search name cannot be empty."),
            ),
            redirect_stdout(output),
        ):
            actions.show_inventory_summary()

        self.assertIn(
            "Enter a product name or return to the main menu.",
            output.getvalue(),
        )

    def test_create_product_displays_duplicate_sku_error(self):
        output = StringIO()
        with (
            patch(
                "builtins.input",
                side_effect=["Another Product", "DUP-001", "12.50", "30"],
            ),
            patch.object(
                actions.product_service,
                "create_product",
                side_effect=ValueError("That SKU already exists."),
            ),
            redirect_stdout(output),
        ):
            actions.create_product_action()

        self.assertIn("That SKU already exists.", output.getvalue())
