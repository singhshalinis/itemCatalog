from catalog_models import Base, User
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from catalog_models import User, Category, Items


engine = create_engine('sqlite:///catalog.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()


# Category functionalities
def getAllCategories():
    cats = session.query(Category).all()
    return cats


def getCategory(cat_id):
    cat = session.query(Category).filter_by(id=cat_id).first()
    return cat


def getCategoryByName(cat_name):
    cat = session.query(Category).filter_by(name=cat_name).first()
    return cat


def addCategory(name, desc, userid):
    cat = Category(name, desc, userid)
    session.add(cat)
    session.commit()


def editCategory(name, desc, cat_id):
    cat = session.query(Category).filter_by(id=cat_id).first()
    return cat


def deleteCategory(cat_id):
    cat = session.query(Category).filter_by(id=cat_id).delete()
    session.commit()


# Item functionalities
def getAllItems():
    items = session.query(Items).all()
    return items


def getAllRecentItems():
    items = session.query(Items).order_by(Items.created.desc()).limit(10)
    return items


def getCategoryItems(category_id):
    items = session.query(Items).filter_by(category_id=category_id).all()
    return items


def getItem(item_id):
    item = session.query(Items).filter_by(id=item_id).first()
    return item


def getItemByNameCat(item_name, cat_id):
    item = session.query(Items).filter_by(category_id=cat_id).filter_by(name=item_name).first()
    return item


def getItemByName(item_name):
    item = session.query(Items).filter_by(name=item_name).first()
    if item:
        return item
    else:
        return None


def addItem(name, desc, category, user_id):
    item = Items(name=name, desc=desc, category=category,
                 category_id=category.id, user_id=user_id)
    session.add(item)
    session.commit()
    return


def updateItem(old_name, name, desc, category):
    dbItem = session.query(Items).filter_by(name=old_name)
    dbItem.update({'name': name, 'category_id': category.id, 'desc': desc})
    session.commit()
    return


def deleteItem(id):
    item = session.query(Items).filter_by(id=id).first()
    session.delete(item)
    session.commit()
    return


# User functionalities
def addNewUser(login_session):
    print 'inside addNewUser'
    print login_session
    newUser = User(name=login_session['username'],
                   email=login_session['email'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).first()
    print user.id
    print user.name
    print "end of addNewUser"
    return user.id


def getUser(user_id):
    user = session.query(User).filter_by(id=user_id).first()
    if user:
        return user
    else:
        None


def getUserId(user_email):
    user = session.query(User).filter_by(email=user_email).first()
    if user:
        return user.id
    else:
        None


def getAllUsers():
    users = session.query(User).all()
    if users:
        return users
    else:
        None
