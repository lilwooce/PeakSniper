from sqlalchemy import Column, String, Integer, BigInteger, DATETIME, Boolean, JSON, FLOAT
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class House(Base):
    __tablename__ = "Houses"

    id = Column("id", Integer, primary_key=True)
    name = Column("name", String(80))
    purchase_value = Column("purchase_value", BigInteger)
    current_value = Column("current_value", BigInteger)
    type_of = Column("type_of", String(80))
    owner = Column("owner", BigInteger)
    daily_expense = Column("daily_expense", BigInteger)
    last_expense_paid = Column("last_expense_paid", DATETIME)
    expenses = Column("expenses", BigInteger)
    bid_history = Column("bid_history", JSON)
    in_market = Column("in_market", Boolean)
    rob_chance = Column("rob_chance", FLOAT)

    def __init__(self, name, purchase_value, type_of, daily_expense):
        self.name = name
        self.purchase_value = purchase_value
        self.current_value = purchase_value
        self.type_of = type_of
        self.owner = 0
        self.daily_expense = daily_expense
        self.last_expense_paid = ""
        self.expenses = 0
        self.in_market = True
        self.bid_history = {}
        self.rob_chance = .01
        
