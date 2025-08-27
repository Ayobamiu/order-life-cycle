from temporalio import workflow
from temporalio import activity
from datetime import timedelta
import uuid

# Import shipping activities (we'll create these next)
from shipping_activities import (
    pick_items_activity,
    package_items_activity,
    select_carrier_activity,
    generate_tracking_activity,
    confirm_delivery_activity,
)


@workflow.defn
class ShippingWorkflow:
    def __init__(self):
        self.cancelled = False
        self.tracking_number = None
        self.carrier = None

    @workflow.run
    async def run(self, order_id: str, items: list) -> dict:
        """Main shipping workflow - processes order from warehouse to delivery"""

        print(f"🚚 Starting ShippingWorkflow for order {order_id}")

        # Step 1: Pick items from warehouse
        print(f"📦 Step 1: Picking items for order {order_id}")
        pick_result = await workflow.execute_activity(
            pick_items_activity,
            args=[order_id, items],
            start_to_close_timeout=timedelta(seconds=30),
        )

        if self.cancelled:
            print(f"❌ Shipping cancelled during picking for {order_id}")
            return {"status": "cancelled", "reason": "Shipping cancelled"}

        # Step 2: Package items
        print(f"📦 Step 2: Packaging items for order {order_id}")
        package_result = await workflow.execute_activity(
            package_items_activity,
            args=[order_id, pick_result],
            start_to_close_timeout=timedelta(seconds=30),
        )

        if self.cancelled:
            print(f"❌ Shipping cancelled during packaging for {order_id}")
            return {"status": "cancelled", "reason": "Shipping cancelled"}

        # Step 3: Select shipping carrier
        print(f"🚛 Step 3: Selecting carrier for order {order_id}")
        carrier_result = await workflow.execute_activity(
            select_carrier_activity,
            args=[order_id, package_result],
            start_to_close_timeout=timedelta(seconds=30),
        )

        self.carrier = carrier_result["carrier"]

        if self.cancelled:
            print(f"❌ Shipping cancelled during carrier selection for {order_id}")
            return {"status": "cancelled", "reason": "Shipping cancelled"}

        # Step 4: Generate tracking number
        print(f"�� Step 4: Generating tracking for order {order_id}")
        tracking_result = await workflow.execute_activity(
            generate_tracking_activity,
            args=[order_id, carrier_result],
            start_to_close_timeout=timedelta(seconds=30),
        )

        self.tracking_number = tracking_result["tracking_number"]

        if self.cancelled:
            print(f"❌ Shipping cancelled during tracking generation for {order_id}")
            return {"status": "cancelled", "reason": "Shipping cancelled"}

        # Step 5: Wait for delivery confirmation (simulated)
        print(f"📋 Step 5: Waiting for delivery confirmation for {order_id}")
        print("⏰ Delivery will take 45 seconds to simulate...")

        if self.cancelled:
            print(f"❌ Shipping cancelled during delivery for {order_id}")
            return {"status": "cancelled", "reason": "Shipping cancelled"}

        # Step 6: Confirm delivery
        print(f"✅ Step 6: Confirming delivery for order {order_id}")
        delivery_result = await workflow.execute_activity(
            confirm_delivery_activity,
            args=[order_id, tracking_result],
            start_to_close_timeout=timedelta(seconds=30),
        )

        print(f"🎉 ShippingWorkflow completed successfully for {order_id}")
        return {
            "status": "delivered",
            "order_id": order_id,
            "tracking_number": self.tracking_number,
            "carrier": self.carrier,
            "delivery_date": delivery_result["delivery_date"],
        }

    # Signal to cancel shipping
    @workflow.signal
    def cancel_shipping_signal(self):
        """Signal to cancel the shipping process"""
        self.cancelled = True
        print("🛑 Shipping cancellation signal received")
