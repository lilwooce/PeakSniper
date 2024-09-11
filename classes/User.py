import json
import random
from sqlalchemy import Column, String, Integer, Boolean, Text, BigInteger, DATETIME, JSON
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
    balance = Column("balance", BigInteger)
    total_earned = Column("total_earned", BigInteger)
    total_lost = Column("total_lost", BigInteger)
    total_bets = Column("total_bets", BigInteger)
    total_gifted = Column("total_gifted", BigInteger)
    total_received = Column("total_received", BigInteger)
    total_snipes = Column("total_snipes", Integer)
    snipe_message = Column("snipe_message", String(200))
    poll_gamba = Column("poll_gamba", BigInteger)
    last_snipe = Column("last_snipe", BigInteger)
    daily_cooldown = Column("daily_cooldown", DATETIME)
    weekly_cooldown = Column("weekly_cooldown", DATETIME)
    steal_cooldown = Column("steal_cooldown", DATETIME)
    interest_cooldown = Column("interest_cooldown", DATETIME)
    injury = Column("injury", DATETIME)
    heist_cooldown = Column("heist_cooldown", DATETIME)
    job = Column("job", String(200))
    inventory = Column("inventory", JSON)
    used_items = Column("used_items", JSON)
    bank = Column("bank", BigInteger)
    portfolio = Column("portfolio", JSON)

    last_worked = Column("last_worked", DATETIME)
    bills = Column("bills", JSON)
    in_jail = Column("in_jail", Boolean)
    reminders = Column("reminders", Boolean)
    freelancers = Column("freelancers", JSON)
    businesses = Column("businesses", JSON)
    revenue = Column("revenue", JSON)

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
        self.total_received = 0
        self.total_snipes = 0
        self.snipe_message = default_snipe_message
        self.poll_gamba = 0
        self.last_snipe = 0
        self.daily_cooldown = ""
        self.weekly_cooldown = ""
        self.steal_cooldown = ""
        self.injury = ""
        self.heist_cooldown = ""
        self.interest_cooldown = ""
        self.job = "beggar"
        self.inventory = {}
        self.used_items = {}
        self.bank = 0
        self.portfolio = {}

        self.in_jail = False
        self.last_worked = ""
        self.bills = {}
        self.businesses = {}
        self.revenue = {}
        self.freelancers = {}
        self.reminders = False

    def get_base_multiplier(self, items):
        multiplier = 0
        # Load used_items from JSON
        used_items = items if items else {}

        for item in used_items:
            if item.type_of == "wealth":
                multiplier += item.boost_amount

        # Check if user has a freelancer with job_type "assistant" and "wealth" in job_name
        for freelancer in self.freelancers:
            if freelancer["job_type"].lower() == "assistant" and "wealth" in freelancer["job_name"].lower():
                multiplier += freelancer.get("boost_amount", 0)
        
        return multiplier
    
    def get_multiplier(self, items, type_of):
        base_multi = self.get_base_multiplier(items)
        multi = 1 + base_multi

        for item in items:
            if item.type_of == type_of:
                multi += item.boost_amount

        for freelancer in self.freelancers:
            if freelancer["job_type"].lower() == "assistant" and type_of in freelancer["job_name"].lower():
                multi += freelancer.get("boost_amount", 0)

        return multi
