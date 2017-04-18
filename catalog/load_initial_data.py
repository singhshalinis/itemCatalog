from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

from catalog_models import User, Category, Items, Base

Base = declarative_base()

engine = create_engine('sqlite:///catalog.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()

# dummy user 1
user1 = User(name='admin', email='admin@xyz.com')
session.add(user1)
session.commit()

cat1 = Category(name='Shoes', desc='Comfort for the journey called life!',
                user_id=user1.id, user=user1)
cat2 = Category(name='Jackets', desc='Keeps you warm', user_id=user1.id,
                user=user1)
cat3 = Category(name='Scarves', desc='Classy and warm!', user_id=user1.id,
                user=user1)
cat4 = Category(name='Bags', desc='Comfortable wherever you go!',
                user_id=user1.id, user=user1)
session.add(cat1)
session.add(cat2)
session.add(cat3)
session.add(cat4)
session.commit()

# item1 = Items(name='Sneakers', desc='Comfortable',
# category=cat1, category_id=cat1.id, user=user1, user_id=user1.id)
# item2 = Items(name='Boots', desc='Comfortable', category=cat1,
# category_id=cat1.id, user=user1, user_id=user1.id)
# session.add(item1)
# session.add(item2)
# session.commit()
