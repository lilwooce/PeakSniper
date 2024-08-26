import json
import random
from sqlalchemy import Column, String, Integer, Boolean, Text, BigInteger, TIMESTAMP, DATETIME, FLOAT
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class ShopItem(Base):
    __tablename__ = "ShopItems"

    id = Column("id", Integer, primary_key=True)
    name = Column("name", String(80))
    price = Column("price", Integer)
    uses = Column("uses", Integer)
    command = Column("command", String(80))
    item_type = Column("item_type", String(80))
    duration = Column("duration", Integer)


    def __init__(self, name, price, uses, command, item_type, duration):
        self.name = name
        self.price = price
        self.uses = uses
        self.command = command
        self.item_type = item_type
        self.duration = duration