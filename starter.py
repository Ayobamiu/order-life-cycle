import asyncio
import uuid
from temporalio.client import Client


async def main():
    client = await Client.connect("localhost:7233")
    order_id = f"order-{uuid.uuid4()}"
    payment_id = f"order-{uuid.uuid4()}"
    print(f"🎯 Starting workflow for order: {order_id}")

    result = await client.execute_workflow(
        "OrderWorkflow",
        args=[order_id, payment_id],
        id=f"workflow-{order_id}",
        task_queue="my-task-queue",
    )
    print(f"✅ Workflow completed! Result:, {result}")


if __name__ == "__main__":
    asyncio.run(main())
