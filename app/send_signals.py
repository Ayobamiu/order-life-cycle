#!/usr/bin/env python3
"""Script to send signals to running workflows"""

import asyncio
from temporalio.client import Client


async def send_cancel_signal(workflow_id: str):
    """Send cancel signal to a running workflow"""
    client = await Client.connect("localhost:7233")

    try:
        # Get workflow handle first, then send signal
        workflow_handle = client.get_workflow_handle(workflow_id)
        await workflow_handle.signal(
            "cancel_order_signal"  # Signal name as string
        )
        print(f"✅ Cancel signal sent to workflow {workflow_id}")
    except Exception as e:
        print(f"❌ Failed to send cancel signal: {str(e)}")


async def send_address_update_signal(workflow_id: str, new_address: dict):
    """Send address update signal to a running workflow"""
    client = await Client.connect("localhost:7233")

    try:
        # Get workflow handle first, then send signal
        workflow_handle = client.get_workflow_handle(workflow_id)
        await workflow_handle.signal(
            "update_address_signal",  # Signal name as string
            new_address,  # Signal arguments
        )
        print(f"✅ Address update signal sent to workflow {workflow_id}")
    except Exception as e:
        print(f"❌ Failed to send address update signal: {str(e)}")


async def main():
    """Main function to demonstrate signals"""
    workflow_id = input("Enter workflow ID to signal: ").strip()

    if not workflow_id:
        print("❌ No workflow ID provided")
        return

    print(f" Sending signals to workflow: {workflow_id}")
    print("1. Cancel order")
    print("2. Update address")
    print("3. Cancel payment")

    choice = input("Choose signal (1-3): ").strip()

    if choice == "1":
        await send_cancel_signal(workflow_id)
    elif choice == "2":
        new_address = {"street": "456 New St", "city": "NewCity", "state": "NY"}
        await send_address_update_signal(workflow_id, new_address)
    elif choice == "3":
        print("Payment cancellation not implemented yet")
    else:
        print("❌ Invalid choice")


if __name__ == "__main__":
    asyncio.run(main())
