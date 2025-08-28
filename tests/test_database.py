"""Unit tests for database operations"""

import pytest
import uuid
from datetime import datetime
from app.models import Order, Payment, Event
from app.database import OrderRepository, PaymentRepository, EventRepository


class TestDatabaseModels:
    """Test database model creation and validation"""

    def test_order_model_creation(self):
        """Test creating an Order model instance"""
        order_id = f"order-{uuid.uuid4()}"
        order = Order(
            id=order_id,
            status="pending",
            customer_name="Test Customer",
            customer_email="test@example.com",
            total_amount=99.99,
            items=[{"sku": "TEST123", "qty": 1, "price": 99.99}],
            shipping_address={
                "street": "123 Test St",
                "city": "Test City",
                "state": "TS",
            },
        )

        assert order.id == order_id
        assert order.status == "pending"
        assert order.customer_name == "Test Customer"
        assert float(order.total_amount) == 99.99
        assert len(order.items) == 1
        assert order.items[0]["sku"] == "TEST123"

    def test_payment_model_creation(self):
        """Test creating a Payment model instance"""
        payment_id = f"payment-{uuid.uuid4()}"
        order_id = f"order-{uuid.uuid4()}"

        payment = Payment(
            id=payment_id,
            order_id=order_id,
            amount=99.99,
            status="pending",
            payment_method="credit_card",
            transaction_id="txn_test_123",
        )

        assert payment.id == payment_id
        assert payment.order_id == order_id
        assert payment.amount == 99.99
        assert payment.status == "pending"
        assert payment.payment_method == "credit_card"

    def test_event_model_creation(self):
        """Test creating an Event model instance"""
        order_id = f"order-{uuid.uuid4()}"

        event = Event(
            order_id=order_id,
            event_type="order_created",
            event_data={"status": "created", "timestamp": "2024-01-01T00:00:00Z"},
            workflow_id="workflow_test_123",
        )

        assert event.order_id == order_id
        assert event.event_type == "order_created"
        assert event.event_data["status"] == "created"
        assert event.workflow_id == "workflow_test_123"


class TestOrderRepository:
    """Test OrderRepository operations"""

    @pytest.fixture
    def db_session(self, test_database):
        """Create a test database session"""
        session = test_database()
        return session

    def test_create_order(self, db_session):
        """Test creating a new order"""
        repo = OrderRepository(db_session)
        order_id = f"order-{uuid.uuid4()}"

        order_data = {
            "id": order_id,
            "status": "pending",
            "customer_name": "Test Customer",
            "customer_email": "test@example.com",
            "total_amount": 99.99,
            "items": [{"sku": "TEST123", "qty": 1, "price": 99.99}],
            "shipping_address": {
                "street": "123 Test St",
                "city": "Test City",
                "state": "TS",
            },
        }

        order = repo.create_order(order_data)

        assert order.id == order_id
        assert order.status == "pending"
        assert order.customer_name == "Test Customer"

        # Verify it was saved to database
        saved_order = db_session.query(Order).filter(Order.id == order_id).first()
        assert saved_order is not None
        assert saved_order.customer_name == "Test Customer"

    def test_get_order(self, db_session):
        """Test retrieving an order by ID"""
        repo = OrderRepository(db_session)
        order_id = f"order-{uuid.uuid4()}"

        # Create an order first
        order_data = {
            "id": order_id,
            "status": "pending",
            "customer_name": "Test Customer",
            "customer_email": "test@example.com",
            "total_amount": 99.99,
            "items": [{"sku": "TEST123", "qty": 1, "price": 99.99}],
            "shipping_address": {
                "street": "123 Test St",
                "city": "Test City",
                "state": "TS",
            },
        }
        repo.create_order(order_data)

        # Retrieve the order
        retrieved_order = repo.get_order(order_id)

        assert retrieved_order is not None
        assert retrieved_order.id == order_id
        assert retrieved_order.customer_name == "Test Customer"

    def test_update_order_status(self, db_session):
        """Test updating order status"""
        repo = OrderRepository(db_session)
        order_id = f"order-{uuid.uuid4()}"

        # Create an order first
        order_data = {
            "id": order_id,
            "status": "pending",
            "customer_name": "Test Customer",
            "customer_email": "test@example.com",
            "total_amount": 99.99,
            "items": [{"sku": "TEST123", "qty": 1, "price": 99.99}],
            "shipping_address": {
                "street": "123 Test St",
                "city": "Test City",
                "state": "TS",
            },
        }
        repo.create_order(order_data)

        # Update the status
        updated_order = repo.update_order_status(order_id, "processing")

        assert updated_order.status == "processing"

        # Verify it was saved to database
        saved_order = db_session.query(Order).filter(Order.id == order_id).first()
        assert saved_order.status == "processing"


class TestPaymentRepository:
    """Test PaymentRepository operations"""

    @pytest.fixture
    def db_session(self, test_database):
        """Create a test database session"""
        session = test_database()
        return session

    def test_create_payment(self, db_session):
        """Test creating a new payment"""
        repo = PaymentRepository(db_session)
        payment_id = f"payment-{uuid.uuid4()}"
        order_id = f"order-{uuid.uuid4()}"

        payment_data = {
            "id": payment_id,
            "order_id": order_id,
            "amount": 99.99,
            "status": "pending",
            "payment_method": "credit_card",
            "transaction_id": "txn_test_123",
        }

        payment = repo.create_payment(payment_data)

        assert payment.id == payment_id
        assert payment.order_id == order_id
        assert float(payment.amount) == 99.99
        assert payment.status == "pending"

        # Verify it was saved to database
        saved_payment = (
            db_session.query(Payment).filter(Payment.id == payment_id).first()
        )
        assert saved_payment is not None
        assert float(saved_payment.amount) == 99.99

    def test_get_payment(self, db_session):
        """Test retrieving a payment by ID"""
        repo = PaymentRepository(db_session)
        payment_id = f"payment-{uuid.uuid4()}"
        order_id = f"order-{uuid.uuid4()}"

        # Create a payment first
        payment_data = {
            "id": payment_id,
            "order_id": order_id,
            "amount": 99.99,
            "status": "pending",
            "payment_method": "credit_card",
            "transaction_id": "txn_test_123",
        }
        repo.create_payment(payment_data)

        # Retrieve the payment
        retrieved_payment = repo.get_payment(payment_id)

        assert retrieved_payment is not None
        assert retrieved_payment.id == payment_id
        assert float(retrieved_payment.amount) == 99.99

    def test_update_payment_status(self, db_session):
        """Test updating payment status"""
        repo = PaymentRepository(db_session)
        payment_id = f"payment-{uuid.uuid4()}"
        order_id = f"order-{uuid.uuid4()}"

        # Create a payment first
        payment_data = {
            "id": payment_id,
            "order_id": order_id,
            "amount": 99.99,
            "status": "pending",
            "payment_method": "credit_card",
            "transaction_id": "txn_test_123",
        }
        repo.create_payment(payment_data)

        # Update the status
        updated_payment = repo.update_payment_status(payment_id, "completed")

        assert updated_payment.status == "completed"

        # Verify it was saved to database
        saved_payment = (
            db_session.query(Payment).filter(Payment.id == payment_id).first()
        )
        assert saved_payment.status == "completed"

    def test_check_payment_idempotency(self, db_session):
        """Test payment idempotency check"""
        repo = PaymentRepository(db_session)
        payment_id = f"payment-{uuid.uuid4()}"
        order_id = f"order-{uuid.uuid4()}"

        # Create a payment first
        payment_data = {
            "id": payment_id,
            "order_id": order_id,
            "amount": 99.99,
            "status": "completed",
            "payment_method": "credit_card",
            "transaction_id": "txn_test_123",
        }
        repo.create_payment(payment_data)

        # Check if payment already exists (idempotency)
        existing_payment = repo.check_payment_exists(payment_id)

        assert existing_payment is not None
        assert existing_payment.id == payment_id
        assert existing_payment.status == "completed"

        # Check non-existent payment
        non_existent_payment = repo.check_payment_exists(f"payment-{uuid.uuid4()}")
        assert non_existent_payment is None


class TestEventRepository:
    """Test EventRepository operations"""

    @pytest.fixture
    def db_session(self, test_database):
        """Create a test database session"""
        session = test_database()
        return session

    def test_log_event(self, db_session):
        """Test logging an event"""
        repo = EventRepository(db_session)
        order_id = f"order-{uuid.uuid4()}"

        event_data = {
            "order_id": order_id,
            "event_type": "order_created",
            "event_data": {"status": "created"},
            "workflow_id": "workflow_test_123",
        }

        event = repo.log_event(event_data)

        assert event.order_id == order_id
        assert event.event_type == "order_created"
        assert event.event_data["status"] == "created"

        # Verify it was saved to database
        saved_event = db_session.query(Event).filter(Event.order_id == order_id).first()
        assert saved_event is not None
        assert saved_event.event_type == "order_created"

    def test_get_order_events(self, db_session):
        """Test retrieving events for an order"""
        repo = EventRepository(db_session)
        order_id = f"order-{uuid.uuid4()}"

        # Create multiple events for the same order
        events_data = [
            {
                "order_id": order_id,
                "event_type": "order_created",
                "event_data": {"status": "created"},
                "workflow_id": "workflow_test_123",
            },
            {
                "order_id": order_id,
                "event_type": "payment_processed",
                "event_data": {"status": "paid"},
                "workflow_id": "workflow_test_123",
            },
            {
                "order_id": order_id,
                "event_type": "shipping_started",
                "event_data": {"status": "shipping"},
                "workflow_id": "workflow_test_123",
            },
        ]

        for event_data in events_data:
            repo.log_event(event_data)

        # Retrieve all events for the order
        order_events = repo.get_order_events(order_id)

        assert len(order_events) == 3
        assert order_events[0].event_type == "order_created"
        assert order_events[1].event_type == "payment_processed"
        assert order_events[2].event_type == "shipping_started"
