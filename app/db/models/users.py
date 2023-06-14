from sqlalchemy import (
    Column,
    DateTime,
    Integer,
    String,
    ARRAY,
    ForeignKey,
    Text,
    Numeric,
    Date,
    func
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

class BaseModel(Base):
    __abstract__ = True
    createdAt = Column(DateTime(timezone=True), default=func.now())
    updatedAt = Column(DateTime(timezone=True), default=func.now(), onupdate=func.now())


class Users(BaseModel):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    fullname = Column(String)
    hashed_password = Column(String)
    date_of_birth = Column(DateTime(timezone=True))
    phone_number = Column(String)
    email = Column(String)
    address = Column(String)
    role = Column(String, default='user')
    reset_password_at = DateTime()
    properties = relationship("Properties", back_populates="users")


class Properties(BaseModel):
    __tablename__ = "properties"
    id = Column(Integer, primary_key=True, index=True)
    address = Column(String)
    area = Column(String)
    images = Column(ARRAY(String))
    user_id = Column(Integer, ForeignKey("users.id"))
    price = Column(Numeric)
    notes = Column(Text)
    users = relationship("Users", back_populates="properties")


class RentalHistory(BaseModel):
    __tablename__ = "rental_history"
    id = Column(Integer, primary_key=True)
    property_id = Column(Integer, ForeignKey("properties.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    transaction_date = Column(Date)

    properties = relationship("Properties", back_populates="rental_history")
    users = relationship("Users", back_populates="rental_history")


class TransactionHistory(BaseModel):
    __tablename__ = "transaction_history"
    id = Column(Integer, primary_key=True)
    property_id = Column(Integer, ForeignKey("properties.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    transaction_date = Column(Date)

    properties = relationship("Properties", back_populates="transaction_history")
    users = relationship("Users", back_populates="transaction_history")
