from fastapi import FastAPI, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from database import Base, engine, get_db
from models import Company, MenuItem, Order, OrderItem
from schemas import (
    MenuItemCreate, MenuItemResponse, OrderCreate,
    OrderStatusUpdate, CompanyCreate, CompanyResponse, OrderResponse
)
from whatsapp import send_whatsapp_message
from datetime import datetime, timedelta
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import joinedload


# Create DB tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="WhatsApp Order Management API")

allow_origins = ["http://localhost:3000", "http://127.0.0.1:3000"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allow_origins,  # ✅ correct variable
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------- Companies ----------------
@app.post("/companies/", response_model=CompanyResponse)
def create_company(company: CompanyCreate, db: Session = Depends(get_db)):
    db_company = Company(
        name=company.name,
        whatsapp_number=company.whatsapp_number,
        api_key=company.api_key
    )
    db.add(db_company)
    db.commit()
    db.refresh(db_company)
    return db_company  # ❌ No WhatsApp message here

# ---------------- Menu Management ----------------
@app.post("/menu/", response_model=MenuItemResponse)
def create_menu_item(
    menu_item: MenuItemCreate,
    db: Session = Depends(get_db),
    api_key: str = Header(None)
):
    company = db.query(Company).filter(Company.api_key == api_key).first()
    if not company:
        raise HTTPException(status_code=401, detail="Invalid API key")

    new_item = MenuItem(
        name=menu_item.name,
        description=menu_item.description,
        price=menu_item.price,
        available=menu_item.available,
        category=menu_item.category,
        company_id=company.id
    )
    db.add(new_item)
    db.commit()
    db.refresh(new_item)
    return new_item

@app.get("/menu/", response_model=list[MenuItemResponse])
def get_menu_items(db: Session = Depends(get_db)):
    return db.query(MenuItem).all()

@app.get("/menu/{item_id}", response_model=MenuItemResponse)
def get_menu_item(item_id: int, db: Session = Depends(get_db)):
    item = db.query(MenuItem).filter(MenuItem.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Menu item not found")
    return item

# ---------------- Orders ----------------
@app.post("/orders/")
def create_order(
    order: OrderCreate,
    db: Session = Depends(get_db),
    api_key: str = Header(None)
):
    company = db.query(Company).filter(Company.api_key == api_key).first()
    if not company:
        raise HTTPException(status_code=401, detail="Invalid API key")

    # Check item availability
    for item in order.items:
        menu_item = db.query(MenuItem).filter(
            MenuItem.id == item.menu_item_id,
            MenuItem.company_id == company.id
        ).first()
        if not menu_item or not menu_item.available:
            raise HTTPException(status_code=400, detail=f"Item {item.menu_item_id} not available")

    new_order = Order(
        customer_name=order.customer_name,
        whatsapp_number=order.whatsapp_number,
        created_at=datetime.utcnow(),
        estimated_delivery=datetime.utcnow() + timedelta(minutes=30),
        company_id=company.id
    )
    db.add(new_order)
    db.commit()
    db.refresh(new_order)

    # Add Order Items
    for item in order.items:
        db.add(OrderItem(
            order_id=new_order.id,
            menu_item_id=item.menu_item_id,
            quantity=item.quantity
        ))
    db.commit()

    # Send WhatsApp confirmation
    total_items = sum([item.quantity for item in order.items])
    message = f"Hello {order.customer_name}, your order #{new_order.id} for {total_items} item(s) has been received! Estimated delivery: {new_order.estimated_delivery}."
    to_number = order.whatsapp_number
    if not to_number.startswith("+"):
        to_number = "+91" + to_number
    send_whatsapp_message(to_number, message)

    return {"order_id": new_order.id, "message": "Order created and WhatsApp notification sent!"}

# ---------------- Order Status Update ----------------
@app.patch("/orders/{order_id}")
def update_order_status(
    order_id: int,
    status_update: OrderStatusUpdate,
    db: Session = Depends(get_db),
    api_key: str = Header(None)
):
    company = db.query(Company).filter(Company.api_key == api_key).first()
    if not company:
        raise HTTPException(status_code=401, detail="Invalid API key")

    order = db.query(Order).filter(Order.id == order_id, Order.company_id == company.id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    order.status = status_update.status
    db.commit()
    db.refresh(order)

    # Send WhatsApp status update
    message = f"Hello {order.customer_name}, your order #{order.id} status has been updated to '{order.status}'."
    to_number = order.whatsapp_number
    if not to_number.startswith("+"):
        to_number = "+91" + to_number
    send_whatsapp_message(to_number, message)

    return {"order_id": order.id, "status": order.status, "message": "WhatsApp notification sent!"}

# ---------------- Retrieve Orders ----------------
@app.get("/orders/", response_model=list[OrderResponse])
def get_orders(db: Session = Depends(get_db)):
    orders = db.query(Order).options(joinedload(Order.items)).all()
    return orders

@app.get("/orders/{order_id}", response_model=OrderResponse)
def get_order(order_id: int, db: Session = Depends(get_db)):
    order = db.query(Order).options(joinedload(Order.items)).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order
# ---------------- Cancel Order ----------------
@app.delete("/orders/{order_id}")
def cancel_order(order_id: int, db: Session = Depends(get_db), api_key: str = Header(None)):
    company = db.query(Company).filter(Company.api_key == api_key).first()
    if not company:
        raise HTTPException(status_code=401, detail="Invalid API key")

    order = db.query(Order).filter(Order.id == order_id, Order.company_id == company.id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    order.status = "canceled"
    db.commit()

    # Send WhatsApp cancellation message
    message = f"Hello {order.customer_name}, your order #{order.id} has been canceled."
    to_number = order.whatsapp_number
    if not to_number.startswith("+"):
        to_number = "+91" + to_number
    send_whatsapp_message(to_number, message)

    return {"order_id": order.id, "status": order.status, "message": "Order canceled and WhatsApp notification sent!"}
