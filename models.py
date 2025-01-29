from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData, Column, String,DateTime,Float, ForeignKey
import uuid
from sqlalchemy_serializer import SerializerMixin
from datetime import datetime

metadata=MetaData()
db=SQLAlchemy(metadata=metadata)

class Order(db.Model,SerializerMixin):
    __tablename__="orders"

    order_id=Column(String, default=lambda:str(uuid.uuid4()) ,nullable=False, primary_key=True, unique=True)
    amount=Column(Float, nullable=False, default=0.00)
    created_at=Column(DateTime, nullable=False, default=datetime.now())
    updated_at=Column(DateTime, nullable=True, onupdate=datetime.now())
    
class Payment(db.Model,SerializerMixin):
    __tablename__="payments"

    id=Column(String, primary_key=True, unique=True, default=lambda:str(uuid.uuid4()), nullable=False)
    amount=Column(Float,nullable=False)
    created_at=Column(DateTime, nullable=False, default=datetime.now())
    updated_at=Column(DateTime, nullable=True, onupdate=datetime.now())
    order_id=Column(String, ForeignKey("orders.order_id"),nullable=False)
    tracking_id=Column(String)
    payment_status=Column(String, default="Pending")
    payment_method=Column(String)
