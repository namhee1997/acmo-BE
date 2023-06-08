from sqlalchemy import Column, DateTime, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class Users(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String)
    hashed_password = Column(String)
    date_of_birth = Column(DateTime(timezone=True))
    phone_number = Column(String)
    email = Column(String)
    address = Column(String)
    reset_password_at = DateTime()
    properties = relationship("Properties", back_populates="user")
