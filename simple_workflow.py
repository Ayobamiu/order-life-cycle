from temporalio import workflow
from datetime import timedelta
from activities import create_order_activity, validate_order_activity


@workflow.defn
class OrderWorkflow:
    @workflow.run
    async def run(self, order_id: str) -> dict:
        print(f"⌛️ Starting OrderWorkflow for {order_id}")

        # Step 1: Create the order
        order_data = await workflow.execute_activity(
            create_order_activity,
            order_id,
            start_to_close_timeout=timedelta(seconds=10),
        )

        # Step 2: Validate the order
        is_valid = await workflow.execute_activity(
            validate_order_activity,
            order_data,
            start_to_close_timeout=timedelta(seconds=10),
        )

        if is_valid:
            print(f"🎉 Order {order_id} workflow completed successfully!")
            return {"status": "success", "order": order_data}
        else:
            print(f"❌ Order {order_id} validation failed!")
            return {"status": "failed", "reason": "validation_error"}
