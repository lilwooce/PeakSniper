import json
import random
from sqlalchemy import Column, String, Integer, Boolean, Text, BigInteger, TIMESTAMP, DATETIME, FLOAT
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Jobs(Base):
    __tablename__ = "Jobs"

    id = Column("id", Integer, primary_key=True)
    name = Column("name", String(80))
    salary = Column("salary", Integer)
    chance = Column("chance", FLOAT)

    def __init__(self, name, salary, chance):
        self.name = name
        self.salary = salary
        self.chance = chance