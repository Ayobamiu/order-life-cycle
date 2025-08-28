from temporalio import activity
from app.database import get_db
from app.models import Order, Payment

from app.function_stubs import (
    order_received,
    order_validated,
    payment_charged,
    order_shipped,
)


@activity.defn
async def validate_order_activity(order_data: dict) -> bool:
    """Validating order data"""
    print(f"✅ Validating order {order_data['order_id']}...")

    db = next(get_db())

    try:
        # Update order status
        return await order_validated(order_data["order_id"], db)

    except Exception as e:
        db.rollback()
        print(f"❌ Failed to validate order {order_data['order_id']}: {str(e)}")
        raise
    finally:
        db.close()


@activity.defn
async def receive_order_activity(order_id: str) -> dict:
    """Create a new order in the database with idempotency"""
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

        # Call the required function stub
        order = await order_received(order_id, db)

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

        result = await payment_charged(order_id=order_id, payment_id=payment_id, db=db)

        print(f"✅ Payment {payment_id} processed for order {order_id}")
        return {
            "payment_id": payment_id,
            "status": result["status"],
            "order_id": order_id,
            "transaction_id": result["transaction_id"],
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
        await order_shipped(order_id, db)
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
