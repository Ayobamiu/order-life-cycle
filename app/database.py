from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import Session
from app.models import Base, Order, Payment, Event


# Database connection string
DATABASE_URL = "postgresql://temporal:temporal@localhost:5432/temporal"

# Create engine
engine = create_engine(DATABASE_URL)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Session:
    """Get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Initialize database tables"""
    Base.metadata.create_all(bind=engine)


class OrderRepository:
    """Repository for Order operations"""

    def __init__(self, db: Session):
        self.db = db

    def create_order(self, order_data: dict) -> Order:
        """Create a new order"""
        order = Order(**order_data)
        self.db.add(order)
        self.db.commit()
        self.db.refresh(order)
        return order

    def get_order(self, order_id: str) -> Order:
        """Get order by ID"""
        return self.db.query(Order).filter(Order.id == order_id).first()

    def update_order_status(self, order_id: str, status: str) -> Order:
        """Update order status"""
        order = self.get_order(order_id)
        if order:
            order.status = status
            self.db.commit()
            self.db.refresh(order)
        return order


class PaymentRepository:
    """Repository for Payment operations"""

    def __init__(self, db: Session):
        self.db = db

    def create_payment(self, payment_data: dict) -> Payment:
        """Create a new payment"""
        payment = Payment(**payment_data)
        self.db.add(payment)
        self.db.commit()
        self.db.refresh(payment)
        return payment

    def get_payment(self, payment_id: str) -> Payment:
        """Get payment by ID"""
        return self.db.query(Payment).filter(Payment.id == payment_id).first()

    def update_payment_status(self, payment_id: str, status: str) -> Payment:
        """Update payment status"""
        payment = self.get_payment(payment_id)
        if payment:
            payment.status = status
            self.db.commit()
            self.db.refresh(payment)
        return payment

    def check_payment_exists(self, payment_id: str) -> Payment:
        """Check if payment already exists (for idempotency)"""
        return self.get_payment(payment_id)


class EventRepository:
    """Repository for Event operations"""

    def __init__(self, db: Session):
        self.db = db

    def log_event(self, event_data: dict) -> Event:
        """Log an event"""
        event = Event(**event_data)
        self.db.add(event)
        self.db.commit()
        self.db.refresh(event)
        return event

    def get_order_events(self, order_id: str) -> list:
        """Get all events for an order"""
        return (
            self.db.query(Event)
            .filter(Event.order_id == order_id)
            .order_by(Event.timestamp)
            .all()
        )


init_db()
