import asyncio
from temporalio.client import Client
from temporalio.worker import Worker
from order_workflow import OrderWorkflow
from activities import (
    validate_order_activity,
    charge_payment_activity,
    receive_order_activity,
    start_shipping_activity,
)


async def main():
    client = await Client.connect("localhost:7233")
    worker = Worker(
        client,
        task_queue="my-task-queue",
        workflows=[OrderWorkflow],
        activities=[
            validate_order_activity,
            charge_payment_activity,
            receive_order_activity,
            start_shipping_activity,
        ],
    )
    print("🚀 Worker started with workflows AND activities!")
    print("Press Ctrl+C to stop the worker")
    await worker.run()


if __name__ == "__main__":
    asyncio.run(main())
