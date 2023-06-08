# pylint: disable=no-name-in-module
# pylint: disable=no-self-argument
from pydantic import BaseModel
import datetime


class Users(BaseModel):
    id = int
    full_name = str
    date_of_birth = datetime
    phone_number = str
    email = str
    address = str

    class Config:
        orm_mode = True


class Properties(BaseModel):
    id = int
    address = str
    area = str
    images = list
    user_id = int
    price = float
    notes = str

    class Config:
        orm_mode = True


class RentalHistory(BaseModel):
    id = int
    property_id = int
    user_id = int
    transaction_date = datetime

    class Config:
        orm_mode = True


class TransactionHistory(BaseModel):
    id = int
    property_id = int
    user_id = int
    transaction_date = datetime

    class Config:
        orm_mode = True
