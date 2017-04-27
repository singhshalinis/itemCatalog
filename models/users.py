from sqlalchemy import Column, ForeignKey, Integer, String, DateTime, Sequence
from sqlalchemy.orm import relationship
from base import BaseModel, session
import datetime

class UserModel(BaseModel):
    __tablename__ = 'users'

    id = Column(Integer, Sequence('user_seq'), primary_key=True)
    username = Column(String(50), nullable=False)
    email = Column(String(50), nullable=False, unique=True)
    image_url = Column(String(50))
    created = Column(DateTime, default=datetime.datetime.now)

    def __init__(self, username, email):
        self.username = username
        self.email = email

    @property
    def easy_serialize(self):
        """Return object data in easily serializeable format"""
        return {
            'username': self.name,
            'email': self.email,
            'image_url': self.image,
        }

    def create_user(self):
        session.add(self)
        session.commit()
        return self
        # return {"message" : "Error creating the user"}

    @classmethod
    def get_by_id(cls, user_id):
        user = session.query(UserModel).filter_by(id=user_id).first()
        if user:
            return user
        # return {"message" : "No user with this user_id"}
        return None

    @classmethod
    def get_by_email(cls, user_email):
        user = session.query(UserModel).filter_by(email=user_email).first()
        if user:
            return user
        # return {"message" : "No user with this email address"}
        return None

    @classmethod
    def get_all(cls):
        users = session.query(UserModel).all()
        if users:
            return users
        return None
