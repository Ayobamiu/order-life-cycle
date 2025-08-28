from temporalio import activity
import uuid
from datetime import datetime


@activity.defn
async def pick_items_activity(order_id: str, items: list) -> dict:
    """Pick items from warehouse"""
    print(f"📦 Picking items for order {order_id}: {items}")

    print("⏳ Simulating warehouse picking...")

    print(f"✅ Items picked for order {order_id}")
    return {
        "order_id": order_id,
        "picked_items": items,
        "picked_at": datetime.utcnow().isoformat(),
        "warehouse_location": "A1-B3-C2",
    }


@activity.defn
async def package_items_activity(order_id: str, pick_result: dict) -> dict:
    """Package picked items"""
    print(f"📦 Packaging items for order {order_id}")
    print(f"✅ Items packaged for order {order_id}")
    return {
        "order_id": order_id,
        "package_weight": 2.5,
        "package_dimensions": "12x8x6 inches",
        "packaged_at": datetime.utcnow().isoformat(),
        "packaging_materials": ["box", "bubble_wrap", "tape"],
    }


@activity.defn
async def select_carrier_activity(order_id: str, package_result: dict) -> dict:
    """Select shipping carrier based on package details"""
    print(f"🚛 Selecting carrier for order {order_id}")

    # Simulate carrier selection logic
    print("⏳ Simulating carrier selection...")

    # Simple carrier selection based on weight
    if package_result["package_weight"] < 5:
        carrier = "USPS"
        service = "Priority Mail"
    else:
        carrier = "FedEx"
        service = "Ground"

    print(f"✅ Carrier selected for order {order_id}: {carrier} - {service}")
    return {
        "order_id": order_id,
        "carrier": carrier,
        "service": service,
        "estimated_days": 3 if carrier == "USPS" else 5,
        "carrier_selected_at": datetime.utcnow().isoformat(),
    }


@activity.defn
async def generate_tracking_activity(order_id: str, carrier_result: dict) -> dict:
    """Generate tracking number for shipment"""
    print(f"🔍 Generating tracking for order {order_id}")

    # Simulate tracking generation
    print("⏳ Simulating tracking generation...")

    # Generate unique tracking number
    tracking_number = f"{carrier_result['carrier']}-{uuid.uuid4().hex[:8].upper()}"

    print(f"✅ Tracking generated for order {order_id}: {tracking_number}")
    return {
        "order_id": order_id,
        "tracking_number": tracking_number,
        "carrier": carrier_result["carrier"],
        "service": carrier_result["service"],
        "tracking_generated_at": datetime.utcnow().isoformat(),
    }


@activity.defn
async def confirm_delivery_activity(order_id: str, tracking_result: dict) -> dict:
    """Confirm delivery of shipment"""
    print(f"✅ Confirming delivery for order {order_id}")

    delivery_date = datetime.utcnow()

    print(f"✅ Delivery confirmed for order {order_id}")
    return {
        "order_id": order_id,
        "delivery_date": delivery_date.isoformat(),
        "delivery_status": "delivered",
        "signature_required": False,
        "delivery_notes": "Left at front door",
    }
