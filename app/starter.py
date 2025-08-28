import asyncio
import uuid
from temporalio.client import Client
from app.order_workflow import OrderWorkflow


async def main():
    client = await Client.connect("localhost:7233")
    id = uuid.uuid4()
    order_id = f"order-{id}"
    payment_id = f"payment-{id}"
    workflow_id = f"workflow-{id}"
    print(f"🎯 Starting workflow for order: {workflow_id}")

    result = await client.execute_workflow(
        OrderWorkflow.run,
        args=[order_id, payment_id],
        id=workflow_id,
        task_queue="my-task-queue",
    )
    print(f"✅ Workflow completed! Result:, {result}")


if __name__ == "__main__":
    asyncio.run(main())
