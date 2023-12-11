from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.core.config import settings

engine = create_engine(str(settings.SQLALCHEMY_DATABASE_URI), pool_pre_ping=True)
# This is used by instancing it
DBSession = sessionmaker(engine, autocommit=False, autoflush=False)
