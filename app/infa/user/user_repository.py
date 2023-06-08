"""User repository module"""
from typing import Optional
from datetime import datetime

from sqlalchemy.orm import Session

from fastapi import Depends

from app.db.models.users import Users

from app.domain.entity import UserInDB
from app.domain.user import UserInCreate, PersonalInUpdate

# from app.shared.utils.general import Users
from sqlalchemy.exc import IntegrityError

from passlib.context import CryptContext



class UserRepository:
    def __init__(self):
        pass

    def create(self, user: UserInCreate, db: Session = Depends(Users)) -> UserInDB:
        """
        Create new user in db
        :param user:
        :return:
        """
        # create user document instance
        try:
            new_user = Users(**user.dict())
            # and save it to db
            db.add(new_user)
            db.commit()

            return UserInDB.from_orm(new_user)
        except IntegrityError:
            db.rollback()
            return None

    def get_by_id(
        self, user_id: str, db: Session = Depends(Users)
    ) -> Optional[UserInDB]:
        """
        Get user in db from id
        :param user_id:
        :return:
        """
        # retrieve unique result
        # https://mongoengine-odm.readthedocs.io/guide/querying.html#retrieving-unique-results
        try:
            user = db.query(Users).filter(Users.id == user_id).first()
        except IntegrityError:
            return None

        return UserInDB.from_orm(user)

    def get_by_email(self, email: str, db: Session = Depends(Users)) -> Optional[UserInDB]:
        """
        Get user in db from email
        :param user_id:
        :return:
        """

        # retrieve unique result
        # https://mongoengine-odm.readthedocs.io/guide/querying.html#retrieving-unique-results
        try:
            user = db.query(Users).filter(Users.email == email).first()
        except IntegrityError:
            return None
        return UserInDB.from_orm(user)

    def update(self, user_id: str, user_update: PersonalInUpdate, db: Session = Depends(Users)) -> UserInDB:
        try:
            update_data = user_update.dict(exclude_unset=True)
            if "token" in update_data:
                del update_data["token"]
            if "code" in update_data:
                update_data["code"] = None
            user = db.query(Users).filter(Users.id == user_id).first()
            if user:
                user.full_name = update_data.full_name
                user.email = update_data.email
                user.date_of_birth = update_data.date_of_birth
                user.phone_number = update_data.phone_number
                user.address = update_data.address
                db.commit()
                db.refresh(user)
            return UserInDB.from_orm(user)
        except IntegrityError as ex:
            raise ex

    def change_password(self, id: str, hashed_password: str, db: Session = Depends(Users)) -> UserInDB:
        try:
            user = db.query(Users).filter(Users.id == id).first()
            password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
            hashed_password = password_context.hash(hashed_password)
            user.hashed_password = hashed_password
            db.commit()
            db.refresh(user)
            return UserInDB.from_orm(user)
        except IntegrityError as ex:
            raise ex

    def update_sent_reset_password(
        self, id: str, updated_at: Optional[datetime], db: Session = Depends(Users)
    ) -> bool:
        try:
            user = db.query(Users).filter(Users.id == id).first()
            user.reset_password_at = updated_at
            db.commit()
            db.refresh(user)
            return True
        except IntegrityError as ex:
            raise ex

    def reset_password(self, id: str, hashed_password: str, db: Session = Depends(Users)) -> True:
        try:
            user = db.query(Users).filter(Users.id == id).first()
            password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
            hashed_password = password_context.hash(hashed_password)
            user.hashed_password = hashed_password
            db.commit()
            db.refresh(user)
            return True
        except IntegrityError as ex:
            raise ex

