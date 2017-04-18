from flask import jsonify
from sqlalchemy import Column, ForeignKey, Integer, String, DateTime, Sequence
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

import datetime
import catalog_CRUD as dataSQL


Base = declarative_base()


class User(Base):
    __tablename__ = 'User'
    id = Column(Integer, Sequence('user_seq'), primary_key=True)
    name = Column(String(50), nullable=False)
    email = Column(String(50), nullable=False, unique=True)
    image_url = Column(String(50))
    # picture =
#    created = Column(DateTime, default=datetime.datetime.now)
    created = Column(String(50))

    @property
    def user_serialize(self):
        """Return object data in easily serializeable format"""
        return {
            'name': self.name,
            'email': self.email,
            'image_url': self.image,
        }


class Category(Base):
    __tablename__ = 'Category'
    id = Column(Integer, Sequence('category_seq'), primary_key=True)
    name = Column(String(50), nullable=False, unique=True)
    desc = Column(String(80))
    created = Column(DateTime, default=datetime.datetime.now)
    created = Column(String(50))
    user_id = Column(Integer, ForeignKey(User.id))
    user = relationship(User)

    @property
    def category_serialize(self):
        """Return object data in easily serializeable format"""

        # get all items for this category
        allitems = dataSQL.getCategoryItems(self.id)
        items = []
        for i in allitems:
            items.append(i.items_serialize)

        str1 = {'id':   self.id,
                'name': self.name,
                'desc': self.desc,
                'Items': items, }
        return str1


class Items(Base):
    __tablename__ = 'Items'
    id = Column(Integer, Sequence('item_seq'), primary_key=True)
    name = Column(String(50), nullable=False, unique=True)
    desc = Column(String(80))
    image_url = Column(String(50))
    created = Column(DateTime, default=datetime.datetime.now)

    category_id = Column(Integer, ForeignKey(Category.id))
    category = relationship(Category)

    user_id = Column(Integer, ForeignKey(User.id))
    user = relationship(User)

    @property
    def items_serialize(self):
        """Return object data in easily serializeable format"""
        return {
            'id': self.id,
            'name': self.name,
            'desc': self.desc,
            'category_id': self.category_id,
        }


# At the end of file
# engine = create_engine('postgresql://scott:tiger@localhost:5432/catalog')
engine = create_engine('sqlite:///catalog.db')
Base.metadata.create_all(engine)
