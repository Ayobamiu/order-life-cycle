import uuid
from temporalio import activity
from database import get_db
from models import Order, Payment, Event


@activity.defn
async def validate_order_activity(order_data: dict) -> bool:
    """Validating order data"""
    print(f"✅ Validating order {order_data['order_id']}...")

    db = next(get_db())

    try:
        # Update order status
        order = db.query(Order).filter(Order.id == order_data["order_id"]).first()
        if order:
            order.status = "validated"
            db.commit()

            # Log event
            event = Event(
                order_id=order_data["order_id"],
                event_type="order_validated",
                event_data={"status": "validated"},
            )
            db.add(event)
            db.commit()

            print(f"✅ Order {order_data['order_id']} validated in database")
            return True
        else:
            print(f"❌ Order {order_data['order_id']} not found in database")
            return False

    except Exception as e:
        db.rollback()
        print(f"❌ Failed to validate order {order_data['order_id']}: {str(e)}")
        raise
    finally:
        db.close()


@activity.defn
async def receive_order_activity(order_id: str) -> dict:
    """Create a new order in the database"""
    print(f"📦 Receiving order {order_id}")

    db = next(get_db())
    try:
        # IDEMPOTENCY CHECK: Check if order already exists
        existing_order = db.query(Order).filter(Order.id == order_id).first()
        if existing_order:
            print(f"✅ Order {order_id} already exists, returning existing result")
            return {
                "order_id": order_id,
                "status": existing_order.status,
                "items": existing_order.items,
                "already_processed": True,
            }

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

        print(f"✅ Order {order_id} created in database")
        return {"order_id": order_id, "status": "received", "items": order.items}

    except Exception as e:
        db.rollback()
        print(f"❌ Failed to create order {order_id}: {str(e)}")
        raise
    finally:
        db.close()


@activity.defn
async def charge_payment_activity(payment_id: str, order_id: str) -> dict:
    """Process payment and save to database"""
    print(f"Charging payment {payment_id} for order {order_id}")

    db = next(get_db())

    try:
        # IDEMPOTENCY CHECK: Check if payment already exists
        existing_payment = db.query(Payment).filter(Payment.id == payment_id).first()
        if existing_payment:
            print(
                f"✅ Payment {payment_id} already processed, returning existing result"
            )
            return {
                "payment_id": payment_id,
                "status": existing_payment.status,
                "order_id": order_id,
                "already_processed": True,
            }

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

        # Update order status
        order = db.query(Order).filter(Order.id == order_id).first()

        if order:
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

        print(f"✅ Payment {payment_id} processed for order {order_id}")
        return {
            "payment_id": payment_id,
            "status": "completed",
            "order_id": order_id,
            "transaction_id": payment.transaction_id,
        }

    except Exception as e:
        db.rollback()
        print(f"❌ Failed to process payment {payment_id}: {str(e)}")
        raise
    finally:
        db.close()


@activity.defn
async def start_shipping_activity(order_id: str) -> dict:
    """Start shipping process and save to database"""
    print(f"🚚 Starting shipping for order {order_id}")

    db = next(get_db())

    try:
        # Update order status to shipping
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

        print(f"✅ Shipping started for order {order_id}")
        return {
            "order_id": order_id,
            "status": "shipping",
            "message": "Shipping process initiated",
        }

    except Exception as e:
        db.rollback()
        print(f"❌ Failed to start shipping for order {order_id}: {str(e)}")
        raise
    finally:
        db.close()
