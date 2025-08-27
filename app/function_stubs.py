import asyncio
import random
from typing import Dict, Any
import uuid

from sqlalchemy.orm import Session

from models import Event, Order, Payment


async def flaky_call() -> None:
    """Either raise an error or sleep long enough to trigger an activity timeout."""
    rand_num = random.random()
    if rand_num < 0.33:
        raise RuntimeError("Forced failure for testing")

    if rand_num < 0.67:
        await asyncio.sleep(
            300
        )  # Expect the activity layer to time out before this completes
    # await asyncio.sleep(3)


async def order_received(order_id: str, db: Session) -> Dict[str, Any]:
    await flaky_call()
    # Create order record
    order = Order(
        id=order_id,
        status="received",
        customer_name="John Doe",
        customer_email="john@example.com",
        total_amount=99.99,
        items=[{"sku": "ABC123", "qty": 1, "price": 99.99}],
        shipping_address={
            "street": "123 Main St",
            "city": "Anytown",
            "state": "CA",
        },
    )
    db.add(order)
    # Log event
    event = Event(
        order_id=order_id,
        event_type="order_received",
        event_data={"status": "created"},
    )
    db.add(event)

    db.commit()
    return order


async def order_validated(order_id: str, db: Session) -> bool:
    await flaky_call()
    order = db.query(Order).filter(Order.id == order_id).first()
    if order:
        order.status = "validated"
        db.commit()

        # Log event
        event = Event(
            order_id=order_id,
            event_type="order_validated",
            event_data={"status": "validated"},
        )
        db.add(event)
        db.commit()
    else:
        print(f"❌ Order {order_id} not found in database")
        return False

    # if hasattr(order, "items"):  # SQLAlchemy Order object
    #     items = order.items
    # else:  # Dictionary
    items = order.items

    if not items:
        raise ValueError("No items to validate")
    return True


async def payment_charged(
    order_id: str, payment_id: str, db: Session
) -> Dict[str, Any]:
    """Charge payment after simulating an error/timeout first.
    You must implement your own idempotency logic in the activity or here.
    """
    await flaky_call()
    # VALIDATION: Check if order exists and is in correct state

    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise ValueError(f"Order {order_id} not found")

    if order.status != "validated":
        raise ValueError(
            f"Order {order_id} is in {order.status} state, cannot process payment"
        )

    # Create payment record
    payment = Payment(
        id=payment_id,
        order_id=order_id,
        amount=99.99,
        status="completed",
        payment_method="credit_card",
        transaction_id=f"txn-{uuid.uuid4()}",
    )
    db.add(payment)

    order.status = "paid"
    db.commit()

    # Log the event
    event = Event(
        order_id=order_id,
        event_type="payment_charged",
        event_data={
            "payment_id": payment_id,
            "status": "completed",
            "transaction_id": payment.transaction_id,
        },
    )
    db.add(event)
    db.commit()
    amount = sum(i.get("qty", 1) for i in order.items)
    return {
        "status": "charged",
        "amount": amount,
        "transaction_id": payment.transaction_id,
    }


async def order_shipped(order_id: str, db: Session) -> str:
    await flaky_call()
    order = db.query(Order).filter(Order.id == order_id).first()
    if order:
        order.status = "shipping"
        # db.add(order)
        db.commit()

    # Create shipping event
    event = Event(
        order_id=order_id,
        event_type="shipping_started",
        event_data={"status": "shipping_initiated"},
    )
    db.add(event)

    db.commit()

    return "Shipped"


async def package_prepared(order_id: str, db: Session) -> str:
    await flaky_call()
    order = db.query(Order).filter(Order.id == order_id).first()
    if order:
        order.status = "package_prepared"
        db.commit()

    event = Event(
        order_id=order_id,
        event_type="package_prepared",
        event_data={"status": "package_prepared"},
    )
    db.add(event)
    db.commit()
    return "Package ready"


async def carrier_dispatched(order_id: str, db: Session) -> str:
    await flaky_call()
    order = db.query(Order).filter(Order.id == order_id).first()
    if order:
        order.status = "carrier_dispatched"
        db.commit()

    event = Event(
        order_id=order_id,
        event_type="carrier_dispatched",
        event_data={"status": "carrier_dispatched"},
    )
    db.add(event)
    db.commit()
    return "Dispatched"
