import json
import random
from sqlalchemy import Column, String, Integer, Boolean, Text, BigInteger, TIMESTAMP, DATETIME, JSON
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Global(Base):
    __tablename__ = "Global"

    id = Column("id", Integer, primary_key=True)
    jobs = Column("jobs", JSON)
    freelancers = Column("freelancers", JSON)



    def __init__(self):
        self.jobs = {"beggar": 10}
        self.freelancers = {"Wealth Creation", "Assistant"}
