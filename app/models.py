from sqlalchemy import Column, String, DateTime, Numeric, Integer, Text, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.postgresql import JSONB


Base = declarative_base()


class Order(Base):
    __tablename__ = "orders"

    id = Column(String(255), primary_key=True)
    status = Column(String(50), nullable=False, default="pending")
    customer_name = Column(String(255))
    customer_email = Column(String(255))
    total_amount = Column(Numeric(10, 2))
    items = Column(JSONB)
    shipping_address = Column(JSONB)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())


class Payment(Base):
    __tablename__ = "payments"

    id = Column(String(255), primary_key=True)
    order_id = Column(String(255), nullable=False)
    amount = Column(Numeric(10, 2), nullable=False)
    status = Column(String(50), nullable=False, default="pending")
    payment_method = Column(String(100))
    transaction_id = Column(String(255))
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())


class Event(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, autoincrement=True)
    order_id = Column(String(255), nullable=False)
    event_type = Column(String(100), nullable=False)
    event_data = Column(JSONB)
    workflow_id = Column(String(255))
    timestamp = Column(DateTime, default=func.now())
