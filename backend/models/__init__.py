from sqlalchemy import ARRAY, BigInteger, Boolean, Column, DateTime,  Index, Integer, Numeric, String, Table, Text, Time, UniqueConstraint, text
from sqlalchemy.dialects.postgresql import INET, JSON, JSONB, OID, TIMESTAMP, UUID
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
metadata = Base.metadata

class User(Base):
    __tablename__ = 'users'

    id = Column(String(64), primary_key=True)
    email = Column(String(255), nullable=False, unique=True)
    user_name = Column(String(255), nullable=False, unique=True)
    password = Column(String(255), nullable=False)
