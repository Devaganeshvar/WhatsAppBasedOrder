# WhatsApp Order Management API

A FastAPI-based backend system that allows restaurants or businesses to manage orders via WhatsApp. Orders can be created, updated, and canceled, with automatic WhatsApp notifications sent to customers using Twilio.

## Features

- Add companies with unique API keys
- Manage menu items for each company
- Create, update, and cancel orders
- Automatic WhatsApp notifications for order updates
- Two-way WhatsApp interaction via webhook (e.g., order cancellation)
- Loyalty points tracking for customers
- Estimated delivery time calculation

## Tech Stack

- **Backend:** Python, FastAPI
- **Database:** MySQL (SQLAlchemy ORM)
- **Notifications:** Twilio WhatsApp API
- **Frontend:** (Optional) React.js
- **Others:** Alembic for migrations, dotenv for environment variables

## Installation

1. Clone the repository:

```bash
git clone https://github.com/Devaganeshvar/WhatsAppBasedOrder.git
cd WhatsAppBasedOrder/backend

2. Create a virtual environment and activate it:
python -m venv venv
# Windows PowerShell
venv\Scripts\Activate.ps1
# macOS/Linux
source venv/bin/activate

3. Install dependencies:
pip install -r requirements.txt

4. Create a .env file in the backend/ directory:
TWILIO_ACCOUNT_SID=your_twilio_sid
TWILIO_AUTH_TOKEN=your_twilio_auth_token
TWILIO_WHATSAPP_NUMBER=+1234567890
DATABASE_URL=mysql+pymysql://user:password@localhost:3306/whatsapp_order_db

5. Run database migrations (if using Alembic):
alembic upgrade head

6.Start the FastAPI server:
uvicorn main:app --reload
The API will be available at http://127.0.0.1:8000.

API Endpoints

POST /companies/ - Add a company

POST /menu/ - Add a menu item

GET /menu/ - List menu items

POST /orders/ - Create an order

PATCH /orders/{order_id} - Update order status

DELETE /orders/{order_id} - Cancel an order

POST /whatsapp/webhook/ - Receive WhatsApp messages (for two-way interaction)
