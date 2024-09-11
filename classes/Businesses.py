from sqlalchemy import Column, String, Integer, BigInteger, DATETIME
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Business(Base):
    __tablename__ = "Businesses"

    id = Column("id", Integer, primary_key=True)
    name = Column("name", String(80))
    purchase_value = Column("purchase_value", BigInteger)
    current_value = Column("current_value", BigInteger)
    type_of = Column("type_of", String(80))
    owner = Column("owner", BigInteger)
    daily_expense = Column("daily_expense", BigInteger)
    daily_revenue = Column("daily_revenue", BigInteger)
    last_expense_paid = Column("last_expense_paid", DATETIME)
    revenue = Column("revenue", BigInteger)
    expenses = Column("expenses", BigInteger)

    def __init__(self, name, purchase_value, type_of, daily_expense, daily_revenue):
        self.name = name
        self.purchase_value = purchase_value
        self.current_value = purchase_value
        self.type_of = type_of
        self.owner = 0
        self.daily_expense = daily_expense
        self.daily_revenue = daily_revenue
        self.last_expense_paid = ""
        self.revenue = 0
        self.expenses = 0
