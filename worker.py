import asyncio
from temporalio.client import Client
from temporalio.worker import Worker
from simple_workflow import OrderWorkflow
from activities import create_order_activity, validate_order_activity


async def main():
    client = await Client.connect("localhost:7233")
    worker = Worker(
        client,
        task_queue="my-task-queue",
        workflows=[OrderWorkflow],
        activities=[create_order_activity, validate_order_activity],
    )
    print("🚀 Worker started with workflows AND activities!")
    print("Press Ctrl+C to stop the worker")
    await worker.run()


if __name__ == "__main__":
    asyncio.run(main())
