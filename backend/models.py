from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime

class Company(Base):
    __tablename__ = "companies"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), unique=True, nullable=False)
    whatsapp_number = Column(String(20), nullable=False)
    api_key = Column(String(100), unique=True, nullable=False)
    menu_items = relationship("MenuItem", back_populates="company", cascade="all, delete")
    orders = relationship("Order", back_populates="company", cascade="all, delete")

class MenuItem(Base):
    __tablename__ = "menu_items"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(String(500))
    price = Column(Float, nullable=False)
    available = Column(Boolean, default=True)
    category = Column(String(100))
    company_id = Column(Integer, ForeignKey("companies.id"))
    company = relationship("Company", back_populates="menu_items")

class Order(Base):
    __tablename__ = "orders"
    id = Column(Integer, primary_key=True, index=True)
    customer_name = Column(String(255), nullable=False)
    whatsapp_number = Column(String(20), nullable=False)
    status = Column(String(50), default="pending")
    created_at = Column(DateTime, default=datetime.utcnow)
    estimated_delivery = Column(DateTime)
    company_id = Column(Integer, ForeignKey("companies.id"))
    company = relationship("Company", back_populates="orders")
    items = relationship("OrderItem", back_populates="order", cascade="all, delete")

class OrderItem(Base):
    __tablename__ = "order_items"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)  
    order_id = Column(Integer, ForeignKey("orders.id"))
    menu_item_id = Column(Integer, ForeignKey("menu_items.id"))
    quantity = Column(Integer)

    order = relationship("Order", back_populates="items")
    menu_item = relationship("MenuItem")
