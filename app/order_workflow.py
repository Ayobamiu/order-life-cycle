from temporalio import workflow
from temporalio.common import RetryPolicy
from datetime import timedelta

from activities import (
    receive_order_activity,
    validate_order_activity,
    charge_payment_activity,
    start_shipping_activity,
)

# Constants - INCREASE THESE FOR TESTING SIGNALS
MANUAL_REVIEW_TIMEOUT = 60  # Increase from 10 to 60 seconds
PAYMENT_PROCESSING_DELAY = 30  # Add 30 second delay for payment
SHIPPING_DELAY = 30  # Add 30 second delay for shipping


@workflow.defn
class OrderWorkflow:
    def __init__(self):
        # Signal state variables
        self.cancelled = False
        self.new_shipping_address = None
        self.payment_cancelled = False

    @workflow.run
    async def run(self, order_id: str, payment_id: str) -> dict:
        """Main order workflow with signal handling"""
        print(f"�� Starting OrderWorkflow for {order_id}")

        try:
            # Step 1: Receive Order
            print(f"Step 1: Receiving order {order_id}")
            order_data = await workflow.execute_activity(
                receive_order_activity,
                order_id,
                start_to_close_timeout=timedelta(seconds=30),
                retry_policy=RetryPolicy(maximum_attempts=3),
            )

            # Check for cancellation after each step
            if self.cancelled:
                print(f"❌ Order {order_id} cancelled during receive step")
                return {"status": "cancelled", "reason": "Order cancelled by customer"}

            # Step 2: Validate Order
            print(f"Step 2: Validating order {order_id}")
            is_valid = await workflow.execute_activity(
                validate_order_activity,
                order_data,
                start_to_close_timeout=timedelta(seconds=30),
                retry_policy=RetryPolicy(maximum_attempts=2),
            )
            if self.cancelled:
                print(f"❌ Order {order_id} cancelled during validation")
                return {"status": "cancelled", "reason": "Order cancelled by customer"}

            if not is_valid:
                return {"status": "failed", "reason": "validation_failed"}

            # Step 3: Manual review with signal checking
            print(f"Step 3: Waiting for manual review approval for {order_id}")
            print(f"⏰ Added {MANUAL_REVIEW_TIMEOUT} seconds to send signals!")

            review_completed = False
            start_time = workflow.now()

            while not review_completed and not self.cancelled:
                # Check for signals every second
                await workflow.sleep(timedelta(seconds=1))

                # Check if review timeout reached
                if workflow.now() - start_time > timedelta(
                    seconds=MANUAL_REVIEW_TIMEOUT
                ):
                    review_completed = True
                    print(f"Manual review completed for {order_id}")

            if self.cancelled:
                print(f"❌ Order {order_id} cancelled during review")
                return {"status": "cancelled", "reason": "Order cancelled by customer"}

            # Step 4: Charge Payment
            if not self.payment_cancelled:
                print(f"Step 4: Charging payment {payment_id} for {order_id}")
                print(
                    f"⏰ Payment processing will take {PAYMENT_PROCESSING_DELAY} seconds..."
                )

                # Add delay before payment processing
                await workflow.sleep(timedelta(seconds=PAYMENT_PROCESSING_DELAY))

                # Check for cancellation during delay
                if self.cancelled:
                    print(f"❌ Order {order_id} cancelled during payment delay")
                    return {
                        "status": "cancelled",
                        "reason": "Order cancelled by customer",
                    }

                await workflow.execute_activity(
                    charge_payment_activity,
                    args=[payment_id, order_id],
                    start_to_close_timeout=timedelta(seconds=30),
                    retry_policy=RetryPolicy(maximum_attempts=3),
                )
            else:
                print(f"❌ Payment cancelled for {order_id}")
                return {
                    "status": "cancelled",
                    "reason": "Payment cancelled by customer",
                }

            if self.cancelled:
                print(f"❌ Order {order_id} cancelled after payment")
                return {"status": "cancelled", "reason": "Order cancelled by customer"}

            # Step 5: Start Shipping Workflow
            print(f"Step 5: Starting shipping workflow for {order_id}")
            print(f"⏰ Shipping setup will take {SHIPPING_DELAY} seconds...")

            # Add delay before shipping
            await workflow.sleep(timedelta(seconds=SHIPPING_DELAY))
            # Check for cancellation during delay
            if self.cancelled:
                print(f"❌ Order {order_id} cancelled during shipping delay")
                return {"status": "cancelled", "reason": "Order cancelled by customer"}

            shipping_result = await workflow.execute_activity(
                start_shipping_activity,
                order_id,
                start_to_close_timeout=timedelta(seconds=30),
                retry_policy=RetryPolicy(maximum_attempts=2),
            )

            # Final status check
            if self.cancelled:
                print(f"❌ Order {order_id} cancelled during shipping")
                return {"status": "cancelled", "reason": "Order cancelled by customer"}

            print(f"🎉 OrderWorkflow completed successfully for {order_id}")
            return {
                "status": "completed",
                "order_id": order_id,
                "shipping_result": shipping_result,
            }

        except Exception as e:
            print(f"💥 OrderWorkflow failed for {order_id}: {str(e)}")
            return {"status": "failed", "reason": "workflow_error", "error": str(e)}

    # Signal definitions
    @workflow.signal
    def cancel_order_signal(self):
        """Signal to cancel the entire order"""
        self.cancelled = True
        print("🛑 Cancel signal received for order workflow")

    @workflow.signal
    def update_address_signal(self, new_address: dict):
        """Signal to update shipping address"""
        self.new_shipping_address = new_address
        print("🏠 Address update signal received: {new_address}")

    @workflow.signal
    def cancel_payment_signal(self):
        """Signal to cancel payment processing"""
        self.payment_cancelled = True
        print("💳 Payment cancellation signal received")
