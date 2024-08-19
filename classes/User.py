import json
import random
from sqlalchemy import Column, String, Integer, Boolean, Text, BigInteger
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

default_snipe_message = "Caught! <:sussykasra:873330894260297759>"

class User(Base):
    __tablename__ = "Users"

    id = Column("id", Integer, primary_key=True)
    name = Column("name", String(80))
    user_id = Column("user_id", BigInteger)
    wins = Column("wins", Integer)
    losses = Column("losses", Integer)
    balance = Column("balance", Integer)
    total_earned = Column("total_earned", Integer)
    total_lost = Column("total_lost", Integer)
    total_bets = Column("total_bets", Integer)
    total_gifted = Column("total_gifted", Integer)
    total_snipes = Column("total_snipes", Integer)
    snipe_message = Column("snipe_message", String(200))

    def __init__(self, user):
        self.name = user.name
        self.user_id = user.id
        self.wins = 0
        self.losses = 0
        self.balance = 0
        self.total_earned = 0
        self.total_lost = 0
        self.total_bets = 0
        self.total_gifted = 0
        self.total_snipes = 0
        self.snipe_message = default_snipe_message
    
    def adjust_snipes(self, user, amount):
        return