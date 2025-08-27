from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any
import uuid
from temporalio.client import Client
from order_workflow import OrderWorkflow

app = FastAPI(title="Order Lifecycle API", version="1.0.0")


# Pydantic models for API requests/responses
class OrderRequest(BaseModel):
    customer_name: str
    customer_email: str
    items: list
    shipping_address: dict


class OrderResponse(BaseModel):
    order_id: str
    workflow_id: str
    status: str
    message: str


class SignalRequest(BaseModel):
    signal_type: str
    data: Optional[Dict[str, Any]] = None


# Global Temporal client
temporal_client: Optional[Client] = None


@app.on_event("startup")
async def startup_event():
    """Initialize Temporal client on startup"""
    global temporal_client
    temporal_client = await Client.connect("localhost:7233")
    print("🚀 Temporal client connected")


@app.on_event("shutdown")
async def shutdown_event():
    """Clean up Temporal client on shutdown"""
    global temporal_client
    if temporal_client:
        # Note: Client doesn't have close() method in this version
        print("🔌 Temporal client shutdown")


@app.post("/orders/{order_id}/start", response_model=OrderResponse)
async def start_order_workflow(order_id: str, request: OrderRequest):
    """Start OrderWorkflow with provided order_id and payment_id"""
    if not temporal_client:
        raise HTTPException(status_code=500, detail="Temporal client not available")

    try:
        # Generate payment ID
        payment_id = f"payment-{uuid.uuid4()}"

        # Start the workflow
        workflow_handle = await temporal_client.start_workflow(
            OrderWorkflow.run,
            args=[order_id, payment_id],
            id=f"workflow-{order_id}",
            task_queue="my-task-queue",
        )

        return OrderResponse(
            order_id=order_id,
            workflow_id=f"workflow-{order_id}",
            status="started",
            message=f"Order workflow started with payment_id: {payment_id}",
        )

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to start workflow: {str(e)}"
        )


@app.post("/orders/{order_id}/signals/cancel")
async def cancel_order(order_id: str):
    """Send CancelOrder signal to running workflow"""
    if not temporal_client:
        raise HTTPException(status_code=500, detail="Temporal client not available")

    try:
        workflow_id = f"workflow-{order_id}"
        workflow_handle = temporal_client.get_workflow_handle(workflow_id)

        # Send cancel signal
        await workflow_handle.signal("cancel_order_signal")

        return {"message": f"Cancel signal sent to order {order_id}"}

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to send cancel signal: {str(e)}"
        )


@app.post("/orders/{order_id}/signals/update-address")
async def update_address(order_id: str, request: SignalRequest):
    """Send UpdateAddress signal to running workflow"""
    if not temporal_client:
        raise HTTPException(status_code=500, detail="Temporal client not available")

    try:
        workflow_id = f"workflow-{order_id}"
        workflow_handle = temporal_client.get_workflow_handle(workflow_id)

        # Send address update signal
        await workflow_handle.signal("update_address_signal", request.data)

        return {"message": f"Address update signal sent to order {order_id}"}

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to send address update signal: {str(e)}"
        )


@app.get("/orders/{order_id}/status")
async def get_order_status(order_id: str):
    """Query OrderWorkflow status to retrieve current state"""
    if not temporal_client:
        raise HTTPException(status_code=500, detail="Temporal client not available")

    try:
        workflow_id = f"workflow-{order_id}"
        workflow_handle = temporal_client.get_workflow_handle(workflow_id)

        # Get workflow status
        status = await workflow_handle.describe()

        return {
            "order_id": order_id,
            "workflow_id": workflow_id,
            "status": status.status.name,
            "run_id": status.run_id,
            "workflow_type": status.workflow_type,
            "start_time": status.start_time.isoformat() if status.start_time else None,
            "close_time": status.close_time.isoformat() if status.close_time else None,
        }

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to get workflow status: {str(e)}"
        )


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "Order Lifecycle API"}
