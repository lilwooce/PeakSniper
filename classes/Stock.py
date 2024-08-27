import json
import random
from sqlalchemy import Column, String, Integer, Boolean, Text, BigInteger, TIMESTAMP, DATETIME, FLOAT
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Stock(Base):
    __tablename__ = "Stocks"

    id = Column("id", Integer, primary_key=True)
    name = Column("name", String(80))
    full_name = Column("full_name", String(255))
    growth_rate = Column("growth_rate", FLOAT)
    current_value = Column("current_value", FLOAT)
    volatility = Column("volatility", FLOAT)
    swap_chance = Column("swap_chance", FLOAT)
    ruination = Column("ruination", FLOAT)
    growth_direction = Column("growth_direction", Integer)
    previous_value = Column("previous_value", FLOAT)
    record_low = Column("record_low", FLOAT)
    record_high = Column("record_high", FLOAT)
    crashed = Column("crashed", Boolean)

    def __init__(self, name, full_name, growth_rate, start_value, volatility, swap_chance, ruination):
            self.name = name
            self.full_name = full_name
            self.growth_rate = growth_rate
            self.current_value = start_value  # Store the actual value as a float
            self.volatility = volatility
            self.swap_chance = swap_chance
            self.ruination = ruination
            self.growth_direction = 1  # 1 for positive growth, -1 for negative
            self.previous_value = start_value
            self.record_low = start_value
            self.record_high = start_value
            self.crashed = False