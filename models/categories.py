from sqlalchemy import Column, ForeignKey, Integer, String, DateTime, Sequence
from sqlalchemy.orm import relationship
from base import BaseModel, session
from users import UserModel
import datetime

class CategoryModel(BaseModel):
    __tablename__ = 'categories'

    id = Column(Integer, Sequence('category_seq'), primary_key=True)
    name = Column(String(50), nullable=False, unique=True)
    desc = Column(String(80))
    created = Column(DateTime, default=datetime.datetime.now)

    #Relationship with User
    user_id = Column(Integer, ForeignKey(UserModel.id))
    user = relationship(UserModel)

    items = relationship('ItemsModel', lazy='dynamic')

    def __init__(self, name, desc, user_id, user):
        self.name = name
        self.desc = desc
        self.user_id = user_id
        self.user = user

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""

        all_items = []
        for i in self.items:
            all_items.append(i.serialize)

        str1 = {'id':   self.id,
                'name': self.name,
                'desc': self.desc,
                'items': all_items, }
        return str1

    def create_category(self):
        session.add(self)
        session.commit()

    def update_category(self, cat_id):
        cat = session.query(CategoryModel).filter_by(id=cat_id).first()
        cat.update({'name': self.name, 'desc': self.desc})
        session.commit()

    def delete_category(self):
        session.delete(self)
        session.commit()

    @classmethod
    def get_all(cls):
        cats = session.query(CategoryModel).all()
        return cats

    @classmethod
    def get_by_id(cls, cat_id):
        cat = session.query(CategoryModel).filter_by(id=cat_id).first()
        if cat:
            return cat
        return None

    @classmethod
    def get_by_name(cls, cat_name):
        cat = session.query(CategoryModel).filter_by(name=cat_name).first()
        if cat:
            return cat
        return None
