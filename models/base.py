from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# database string
db_string = "postgresql://postgres:postgres@localhost:5432/catalog"

BaseModel = declarative_base()

# At the end of file
# engine = create_engine('postgresql://scott:tiger@localhost:5432/catalog')
# engine = create_engine('sqlite:///catalog.db')
engine = create_engine(db_string)
# BaseModel.metadata.create_all(engine)
BaseModel.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()
