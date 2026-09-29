from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base


SQL_ALCHEMY_DATABASE_URL="sqlite:///./expense_tracker.db"
engine=create_engine(SQL_ALCHEMY_DATABASE_URL)

sessionlocal=sessionmaker(autoflush=False,autocommit=False,bind=engine)
Base=declarative_base()
