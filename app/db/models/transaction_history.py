from sqlalchemy import Column, ForeignKey, Integer, Date
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class TransactionHistory(Base):
    __tablename__ = 'transaction_history'
    id = Column(Integer, primary_key=True)
    property_id = Column(Integer, ForeignKey('properties.id'))
    user_id = Column(Integer, ForeignKey('users.id'))
    transaction_date = Column(Date)

    property = relationship("Properties", back_populates="transaction_history")
    user = relationship("Users", back_populates="transaction_history")




