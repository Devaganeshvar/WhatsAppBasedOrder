import uuid
from fastapi.testclient import TestClient
from unittest.mock import patch
from main import app
from database import Base, engine, get_db
from sqlalchemy.orm import sessionmaker
from models import Company, MenuItem, Order, OrderItem
from schemas import MenuItemCreate, OrderCreate, OrderItemCreate, OrderStatusUpdate

# ---------------- Setup test database session ----------------
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base.metadata.create_all(bind=engine)

def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)

# ---------------- Mock WhatsApp messaging ----------------
@patch("whatsapp.send_whatsapp_message")
def test_sdk_style_flow(mock_whatsapp):
    # ---------------- Generate unique values ----------------
    api_key = str(uuid.uuid4())
    company_name = f"Test Restaurant {uuid.uuid4()}"
    customer_name = "John Doe"
    whatsapp_number = "+917010973101"

    # -------- Create Company --------
    company_resp = client.post("/companies/", json={
        "name": company_name,
        "whatsapp_number": whatsapp_number,
        "api_key": api_key
    })
    assert company_resp.status_code == 200
    print("✅ Company created:", company_resp.json())

    headers = {"api-key": api_key}

    # -------- Add Menu Item --------
    menu_item_name = f"Cheese Pizza {uuid.uuid4()}"
    menu_item = MenuItemCreate(
        name=menu_item_name,
        description="Delicious cheese pizza",
        price=299.0,
        available=True,
        category="Fast Food"
    )
    menu_resp = client.post("/menu/", json=menu_item.dict(), headers=headers)
    assert menu_resp.status_code == 200
    menu_id = menu_resp.json()["id"]
    print("✅ Menu item created:", menu_resp.json())

    # -------- Place Order --------
    order_data = OrderCreate(
        customer_name=customer_name,
        whatsapp_number=whatsapp_number,
        items=[OrderItemCreate(menu_item_id=menu_id, quantity=2)]
    )
    order_resp = client.post("/orders/", json=order_data.dict(), headers=headers)
    assert order_resp.status_code == 200
    order_id = order_resp.json()["order_id"]
    print("✅ Order placed:", order_resp.json())

    # Ensure WhatsApp message sent
    mock_whatsapp.assert_called()

    # -------- Update Order Status --------
    status_update = OrderStatusUpdate(status="delivered")
    status_resp = client.patch(f"/orders/{order_id}", json=status_update.dict(), headers=headers)
    assert status_resp.status_code == 200
    print("✅ Order status updated:", status_resp.json())

    # -------- List All Orders --------
    all_orders_resp = client.get("/orders/", headers=headers)
    assert all_orders_resp.status_code == 200
    print("📋 All orders:", all_orders_resp.json())

    # -------- Get Order by ID --------
    order_detail_resp = client.get(f"/orders/{order_id}", headers=headers)
    assert order_detail_resp.status_code == 200
    print("🔍 Order details:", order_detail_resp.json())

    print("✅ SDK-style test flow completed successfully!")
