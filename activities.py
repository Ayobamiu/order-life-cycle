from temporalio import activity


@activity.defn
async def create_order_activity(order_id: str) -> dict:
    """Simulates creating an order in a database"""
    print(f"🏗️ Creating order {order_id} in database...")

    # Simulate some work
    order_data = {
        "order_id": order_id,
        "status": "created",
        "items": ["item1", "item2"],
        "created_at": "2024-01-01",
    }

    print(f"✅ Order {order_id} created successfully!")
    return order_data


@activity.defn
async def validate_order_activity(order_data: dict) -> bool:
    """Simulates validating an order"""
    print(f"�� Validating order {order_data['order_id']}...")

    # Simulate validation logic
    if order_data["items"]:
        print(f"✅ Order {order_data['order_id']} is valid!")
        return True
    else:
        print(f"❌ Order {order_data['order_id']} has no items!")
        return False
