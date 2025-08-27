from temporalio import workflow
from temporalio.common import RetryPolicy
from datetime import timedelta
from activities import create_order_activity, validate_order_activity


@workflow.defn
class OrderWorkflow:
    @workflow.run
    async def run(self, order_id: str) -> dict:
        print(f"⌛️ Starting OrderWorkflow for {order_id}")

        try:
            retry_policy_one = RetryPolicy(
                maximum_attempts=3,  # Try up to 3 times
                initial_interval=timedelta(
                    seconds=1
                ),  # Wait 1 second before first retry
                maximum_interval=timedelta(seconds=5),  # Max 5 seconds between retries
            )

            # Step 1: Create the order
            order_data = await workflow.execute_activity(
                create_order_activity,
                order_id,
                start_to_close_timeout=timedelta(seconds=10),
                retry_policy=retry_policy_one,
            )

            retry_policy_two = RetryPolicy(
                maximum_attempts=2,  # Try up to 2 times
                initial_interval=timedelta(seconds=1),  # Wait 1 second before retry
            )

            # Step 2: Validate the order
            is_valid = await workflow.execute_activity(
                validate_order_activity,
                order_data,
                start_to_close_timeout=timedelta(seconds=10),
                retry_policy=retry_policy_two,
            )

            if is_valid:
                print(f"🎉 Order {order_id} workflow completed successfully!")
                return {"status": "success", "order": order_data}
            else:
                print(f"❌ Order {order_id} validation failed!")
                return {"status": "failed", "reason": "validation_error"}
        except Exception as e:
            print(f"💥 Workflow failed for order {order_id}: {str(e)}")
            return {"status": "failed", "reason": "workflow_error", "error": str(e)}
