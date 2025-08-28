"""Unit tests for Temporal activities"""

import pytest
import uuid
from unittest.mock import patch, MagicMock
from app.activities import (
    receive_order_activity,
    validate_order_activity,
    start_shipping_activity,
)


class TestReceiveOrderActivity:
    """Test receive_order_activity"""

    @pytest.mark.asyncio
    async def test_receive_order_activity_success(self, test_database):
        """Test successful order creation"""
        order_id = f"order-{uuid.uuid4()}"

        # Mock the database session and flaky_call
        with (
            patch("app.activities.get_db") as mock_get_db,
            patch("app.function_stubs.flaky_call") as mock_flaky_call,
        ):
            # Mock flaky_call to succeed
            mock_flaky_call.return_value = None

            mock_db = MagicMock()
            mock_get_db.return_value = iter([mock_db])

            # Mock the order query
            mock_db.query.return_value.filter.return_value.first.return_value = None

            result = await receive_order_activity(order_id)

            # Verify the result
            assert result["order_id"] == order_id
            assert result["status"] == "received"
            assert "items" in result

            # Verify database operations were called
            mock_db.add.assert_called()
            mock_db.commit.assert_called()


class TestValidateOrderActivity:
    """Test validate_order_activity"""

    @pytest.mark.asyncio
    async def test_validate_order_activity_success(self, test_database):
        """Test successful order validation"""
        order_id = f"order-{uuid.uuid4()}"
        order_data = {"order_id": order_id}

        with (
            patch("app.activities.get_db") as mock_get_db,
            patch("app.function_stubs.flaky_call") as mock_flaky_call,
        ):
            # Mock flaky_call to succeed
            mock_flaky_call.return_value = None

            mock_db = MagicMock()
            mock_get_db.return_value = iter([mock_db])

            # Mock existing order
            mock_order = MagicMock()
            mock_order.id = order_id
            mock_order.status = "received"
            mock_order.items = [{"sku": "TEST123", "qty": 1}]
            mock_order.customer_name = "Test Customer"
            mock_order.total_amount = 25.00

            mock_db.query.return_value.filter.return_value.first.return_value = (
                mock_order
            )

            result = await validate_order_activity(order_data)

            assert result is True

    @pytest.mark.asyncio
    async def test_validate_order_activity_order_not_found(self, test_database):
        """Test validation with non-existent order"""
        order_id = f"order-{uuid.uuid4()}"
        order_data = {"order_id": order_id}

        with (
            patch("app.activities.get_db") as mock_get_db,
            patch("app.function_stubs.flaky_call") as mock_flaky_call,
        ):
            # Mock flaky_call to succeed
            mock_flaky_call.return_value = None

            mock_db = MagicMock()
            mock_get_db.return_value = iter([mock_db])

            # Mock no order found
            mock_db.query.return_value.filter.return_value.first.return_value = None

            result = await validate_order_activity(order_data)

            assert result is False


class TestStartShippingActivity:
    """Test start_shipping_activity"""

    @pytest.mark.asyncio
    async def test_start_shipping_activity_success(self, test_database):
        """Test successful shipping start"""
        order_id = f"order-{uuid.uuid4()}"

        with (
            patch("app.activities.get_db") as mock_get_db,
            patch("app.function_stubs.flaky_call") as mock_flaky_call,
        ):
            # Mock flaky_call to succeed
            mock_flaky_call.return_value = None

            mock_db = MagicMock()
            mock_get_db.return_value = iter([mock_db])

            # Mock existing order
            mock_order = MagicMock()
            mock_order.id = order_id
            mock_order.status = "payment_completed"

            mock_db.query.return_value.filter.return_value.first.return_value = (
                mock_order
            )

            result = await start_shipping_activity(order_id)

            assert result["order_id"] == order_id
            assert result["status"] == "shipping"
            assert "message" in result

            # Verify database operations were called
            mock_db.commit.assert_called()
