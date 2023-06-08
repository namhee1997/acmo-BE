from sqlalchemy import Column, ForeignKey, Integer, String, ARRAY, Numeric, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class Properties(Base):
    __tablename__ = "properties"
    id = Column(Integer, primary_key=True, index=True)
    address = Column(String)
    area = Column(String)
    images = Column(ARRAY(String))
    user_id = Column(Integer, ForeignKey("users.id"))
    price = Column(Numeric)
    notes = Column(Text)
    user = relationship("Users", back_populates="properties")



