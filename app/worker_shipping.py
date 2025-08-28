import asyncio
from temporalio.client import Client
from temporalio.worker import Worker
from app.shipping_workflow import ShippingWorkflow
from app.shipping_activities import (
    pick_items_activity,
    package_items_activity,
    select_carrier_activity,
    generate_tracking_activity,
    confirm_delivery_activity,
)


async def main():
    client = await Client.connect("localhost:7233")

    # Create worker for shipping workflows and activities
    worker = Worker(
        client,
        task_queue="shipping-task-queue",
        workflows=[ShippingWorkflow],
        activities=[
            pick_items_activity,
            package_items_activity,
            select_carrier_activity,
            generate_tracking_activity,
            confirm_delivery_activity,
        ],
    )

    print("🚚 Shipping worker started!")
    print("Press Ctrl+C to stop the worker")

    await worker.run()


if __name__ == "__main__":
    asyncio.run(main())
