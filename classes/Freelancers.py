from sqlalchemy import Column, Integer, String, BigInteger, FLOAT, Boolean
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Freelancer(Base):
    __tablename__ = "Freelancers"

    id = Column("id", Integer, primary_key=True)
    name = Column("name", String)
    job_title = Column("job_title", String)
    initial_cost = Column("initial_cost", Integer)
    daily_expense = Column("daily_expense", Integer)
    type_of = Column("type_of", String)
    boss = Column("boss", BigInteger)
    poach_minimum = Column("poach_minimum", BigInteger)
    expense = Column("expense", BigInteger)
    is_free = Column("is_free", Boolean)
    expense = Column("expense", FLOAT)

    def __init__(self, name, job_title, initial_cost, daily_expense, type_of, boss, poach_minimum, boost_amount):
        self.name = name
        self.job_title = job_title
        self.initial_cost = initial_cost
        self.daily_expense = daily_expense
        self.type_of = type_of
        self.boss = boss
        self.poach_minimum = poach_minimum
        self.expense = 0
        self.is_free = True
        self.boost_amount = boost_amount
