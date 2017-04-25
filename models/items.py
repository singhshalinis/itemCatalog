from sqlalchemy import Column, ForeignKey, Integer, String, DateTime, Sequence
from sqlalchemy.orm import relationship
from base import BaseModel, session
from users import UserModel
from categories import CategoryModel
import datetime

class ItemsModel(BaseModel):
    __tablename__ = 'items'

    id = Column(Integer, Sequence('item_seq'), primary_key=True)
    name = Column(String(50), nullable=False, unique=True)
    desc = Column(String(80))
    image_url = Column(String(50))
    created = Column(DateTime, default=datetime.datetime.now)

    #Relationship with category
    category_id = Column(Integer, ForeignKey(CategoryModel.id))
    category = relationship(CategoryModel)

    #Relationship with User
    user_id = Column(Integer, ForeignKey(UserModel.id))
    user = relationship(UserModel)

    def __init__(self, name, desc, category_id, user_id):
        self.name = name
        self.desc = desc
        self.category_id = category_id
        self.user_id = user_id

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
            'id': self.id,
            'name': self.name,
            'desc': self.desc,
            'category_id': self.category_id,
            }

    def save_to_db(self):
        session.add(self)
        session.commit()

    def update_item(self):
        # dbItem = session.query(ItemsModel).filter_by(id=item_id)
        # dbItem.update({'name': self.name, 'category_id': self.category.id, 'desc': self.desc})
        # session.commit()
        pass

    def delete_item(self):
        session.delete(self)
        session.commit()

    @classmethod
    def get_by_id(cls, item_id):
        item = session.query(ItemsModel).filter_by(id=item_id).first()
        if item:
            return item
        return None

    @classmethod
    def get_by_name(cls, item_name):
        item = session.query(ItemsModel).filter_by(name=item_name).first()
        if item:
            return item
        return None

    @classmethod
    def get_by_name_and_category(cls, item_name, cat_id):
        item = session.query(ItemsModel).filter_by(category_id=cat_id).filter_by(name=item_name).first()
        if item:
            return item
        return None

    @classmethod
    def get_all(cls):
        items = session.query(ItemsModel).all()
        return items

    @classmethod
    def get_new_items(cls):
        items = session.query(ItemsModel).order_by(ItemsModel.created.desc()).limit(10)
        return items

    @classmethod
    def get_all_in_a_category(cls, category_id):
        items = session.query(ItemsModel).filter_by(category_id=category_id).all()
        return items
