from temporalio import workflow
from temporalio.common import RetryPolicy
from datetime import timedelta
from activities import (
    receive_order_activity,
    validate_order_activity,
    charge_payment_activity,
    start_shipping_activity,
)


@workflow.defn
class OrderWorkflow:
    @workflow.run
    async def run(self, order_id: str, payment_id: str) -> dict:
        print(f"�� Starting OrderWorkflow for {order_id}")

        try:
            # Step 1: Receive Order
            print(f"Step 1: Receiving order {order_id}")
            order_data = await workflow.execute_activity(
                receive_order_activity,
                order_id,
                start_to_close_timeout=timedelta(seconds=5),
                retry_policy=RetryPolicy(maximum_attempts=3),
            )

            # Step 2: Validate Order
            print(f"Step 2: Validating order {order_id}")
            is_valid = await workflow.execute_activity(
                validate_order_activity,
                order_data,
                start_to_close_timeout=timedelta(seconds=5),
                retry_policy=RetryPolicy(maximum_attempts=2),
            )

            if not is_valid:
                return {"status": "failed", "reason": "validation_failed"}

            # Step 3: Manual Review Timer (simulated)
            print(f"Step 3: Waiting for manual review approval for {order_id}")
            await workflow.sleep(timedelta(seconds=3))  # Simulate 3-second review
            print(f"Manual review completed for {order_id}")

            # Step 4: Charge Payment
            print(f"Step 4: Charging payment {payment_id} for {order_id}")
            payment_result = await workflow.execute_activity(
                charge_payment_activity,
                args=[order_id, payment_id],
                start_to_close_timeout=timedelta(seconds=5),
                retry_policy=RetryPolicy(maximum_attempts=3),
            )

            # Step 5: Start Shipping Workflow
            print(f"Step 5: Starting shipping workflow for {order_id}")
            shipping_result = await workflow.execute_activity(
                start_shipping_activity,
                order_id,
                start_to_close_timeout=timedelta(seconds=5),
                retry_policy=RetryPolicy(maximum_attempts=2),
            )

            # Step 6: Complete
            print(f"🎉 OrderWorkflow completed successfully for {order_id}")
            return {
                "status": "success",
                "order": order_data,
                "payment": payment_result,
                "shipping": shipping_result,
            }

        except Exception as e:
            print(f"💥 OrderWorkflow failed for {order_id}: {str(e)}")
            return {"status": "failed", "reason": "workflow_error", "error": str(e)}
