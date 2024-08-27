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
    
    def update(self):
        # Check for ruination (complete crash)
        if random.random() < self.ruination and not self.crashed:
            self.current_value = 5
            self.crashed = True
            self.record_low = min(self.record_low, self.current_value)
            return

        # Chance of swapping growth direction
        if random.random() < self.swap_chance:
            self.growth_direction *= -1

        # Update the stock price based on growth rate and volatility
        self.previous_value = self.current_value
        change = self.current_value * self.growth_rate * self.growth_direction
        volatility_effect = self.current_value * self.volatility * (random.random() - 0.5)
        self.current_value += change + volatility_effect

        # Ensure the price doesn't drop below zero
        if self.current_value < 5:
            self.current_value = 5

        # Update record low and high
        self.record_low = min(self.record_low, self.current_value)
        self.record_high = max(self.record_high, self.current_value)

        # After the first update post-crash, remove the crashed flag
        if self.crashed:
            self.crashed = False

    def get_percentage_change(self):
        # Calculate the percentage change
        if self.previous_value == 0:
            return 0
        return ((self.current_value - self.previous_value) / self.previous_value) * 100

    def is_stable(self):
        # Determine if the stock is stable or unstable based on thresholds
        volatility_threshold = 0.04  # Example threshold for volatility
        swap_chance_threshold = 0.05  # Example threshold for swap chance

        if self.volatility > volatility_threshold or self.swap_chance > swap_chance_threshold:
            return "unstable"
        else:
            return "stable"

    def __str__(self):
        percent_change = self.get_percentage_change()
        direction = "up" if percent_change > 0 else "down"
        stability = self.is_stable()
        display_value = int(self.current_value)  # Display the integer part of the value

        # Show "Crashed" if the stock just crashed in the current update
        if self.crashed:
            return f"{self.full_name} ({self.name}): {display_value} đ (Crashed)"
        
        return f"{self.full_name} ({self.name}): {display_value} đ ({abs(percent_change):.2f}% {direction}, {stability}, {self.growth_direction})"