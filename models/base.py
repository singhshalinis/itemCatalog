from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

BaseModel = declarative_base()

# At the end of file
# engine = create_engine('postgresql://scott:tiger@localhost:5432/catalog')
# engine = create_engine('sqlite:///catalog.db')
engine = create_engine('sqlite:///catalog01.db')
# BaseModel.metadata.create_all(engine)
BaseModel.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()
