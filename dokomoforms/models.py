"""Question model"""

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String

Base = declarative_base()


class Question(Base):
    __tablename__ = 'question'

    id = Column(Integer, primary_key=True)
    name = Column(String)
