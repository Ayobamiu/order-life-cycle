"""Pytest configuration and fixtures for Temporal Order Lifecycle testing"""

import pytest
import asyncio
import tempfile
import os
from temporalio.testing import WorkflowEnvironment
from temporalio.client import Client
from temporalio.worker import Worker
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Import your application components
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from app.models import Base
from app.activities import (
    receive_order_activity,
    validate_order_activity,
    charge_payment_activity,
    start_shipping_activity,
)
from app.shipping_activities import (
    pick_items_activity,
    package_items_activity,
    select_carrier_activity,
    generate_tracking_activity,
    confirm_delivery_activity,
)
from app.order_workflow import OrderWorkflow
from app.shipping_workflow import ShippingWorkflow


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
async def temporal_environment():
    """Create a Temporal test environment."""
    env = await WorkflowEnvironment.start_local()
    yield env
    await env.shutdown()


@pytest.fixture
async def temporal_client(temporal_environment):
    """Create a Temporal client connected to the test environment."""
    client = await Client.connect("localhost:7233")
    return client


@pytest.fixture
async def order_worker(temporal_client):
    """Create a worker for order workflows and activities."""
    worker = Worker(
        temporal_client,
        task_queue="test-order-queue",
        workflows=[OrderWorkflow],
        activities=[
            receive_order_activity,
            validate_order_activity,
            charge_payment_activity,
            start_shipping_activity,
        ],
    )

    # Start the worker
    worker_run = asyncio.create_task(worker.run())
    return worker


@pytest.fixture
async def shipping_worker(temporal_client):
    """Create a worker for shipping workflows and activities."""
    worker = Worker(
        temporal_client,
        task_queue="test-shipping-queue",
        workflows=[ShippingWorkflow],
        activities=[
            pick_items_activity,
            package_items_activity,
            select_carrier_activity,
            generate_tracking_activity,
            confirm_delivery_activity,
        ],
    )

    # Start the worker
    worker_run = asyncio.create_task(worker.run())
    return worker


@pytest.fixture
def test_database():
    """Create a test database in memory."""
    # Use SQLite for testing (faster than PostgreSQL)
    engine = create_engine("sqlite:///:memory:")

    # Create test-specific models with SQLite-compatible types
    from sqlalchemy import Column, String, DateTime, Numeric, Integer, Text, JSON, func
    from sqlalchemy.ext.declarative import declarative_base

    TestBase = declarative_base()

    class TestOrder(TestBase):
        __tablename__ = "orders"
        id = Column(String(255), primary_key=True)
        status = Column(String(50), nullable=False, default="pending")
        customer_name = Column(String(255))
        customer_email = Column(String(255))
        total_amount = Column(Numeric(10, 2))
        items = Column(JSON)  # Use JSON instead of JSONB for SQLite
        shipping_address = Column(JSON)
        created_at = Column(DateTime, default=func.now())
        updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    class TestPayment(TestBase):
        __tablename__ = "payments"
        id = Column(String(255), primary_key=True)
        order_id = Column(String(255), nullable=False)
        amount = Column(Numeric(10, 2), nullable=False)
        status = Column(String(50), nullable=False, default="pending")
        payment_method = Column(String(100))
        transaction_id = Column(String(255))
        created_at = Column(DateTime, default=func.now())
        updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    class TestEvent(TestBase):
        __tablename__ = "events"
        id = Column(Integer, primary_key=True, autoincrement=True)
        order_id = Column(String(255), nullable=False)
        event_type = Column(String(100), nullable=False)
        event_data = Column(JSON)  # Use JSON instead of JSONB for SQLite
        workflow_id = Column(String(255))
        timestamp = Column(DateTime, default=func.now())

    # Create all tables
    TestBase.metadata.create_all(bind=engine)

    # Create session factory
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    yield TestingSessionLocal

    # Cleanup
    engine.dispose()


@pytest.fixture
def sample_order_data():
    """Sample order data for testing."""
    return {
        "customer_name": "Test Customer",
        "customer_email": "test@example.com",
        "items": [{"sku": "TEST123", "qty": 2, "price": 25.00}],
        "shipping_address": {
            "street": "123 Test St",
            "city": "Test City",
            "state": "TS",
        },
    }


@pytest.fixture
def sample_payment_data():
    """Sample payment data for testing."""
    return {
        "amount": 50.00,
        "payment_method": "credit_card",
        "transaction_id": "txn_test_123",
    }
