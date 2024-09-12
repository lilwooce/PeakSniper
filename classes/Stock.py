import json
import random
from sqlalchemy import Column, String, Integer, Boolean, Text, BigInteger, TIMESTAMP, DATETIME, FLOAT, JSON
from sqlalchemy.ext.declarative import declarative_base
import matplotlib.pyplot as plt
from sqlalchemy.ext.mutable import MutableList
import base64
import io
import logging

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
    history = Column("history", MutableList.as_mutable(JSON))
    type_of = Column("type_of", String(80))
    amount = Column("amount", Integer)

    def __init__(self, name, full_name, growth_rate, start_value, volatility, swap_chance, ruination, type_of):
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
            self.history = [self.current_value]
            self.type_of = type_of
            self.amount = self.determine_stock_amount()

    def determine_stock_amount(self, baseline_net_worth=2622406):
        # Random factor between 0.8 and 1.2
        random_factor = random.uniform(0.8, 1.2)
        
        # Adjust for volatility and growth rate
        volatility_factor = max(0.5, 1 - self.volatility)  # Higher volatility means lower amount
        growth_factor = 1 + (self.growth_rate / 10)  # Higher growth means slightly higher amount
        
        # Calculate the stock amount, adjusting for stock's current value
        amount = (baseline_net_worth / self.current_value) * random_factor * volatility_factor * growth_factor
        logging.warning(f"Starting amount: {amount} (based on current value: {self.current_value})")
        
        return int(amount)


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
        self.history.append(self.current_value)

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
    
    def graph(self):
        # Generate the graph and save it as a base64-encoded string
        # Ensure that self.history is not empty and has numeric values
        if not self.history or not all(isinstance(value, (int, float)) for value in self.history):
            raise ValueError("History data must be a list of numeric values and cannot be empty.")

        # Generate the graph and save it as a base64-encoded string
        plt.figure(figsize=(6, 4))
        
        # Plot the history data
        plt.plot(range(len(self.history)), self.history, label=self.name)  # Use range to create x-axis values

        # Set axis limits
        # plt.axis([0, len(self.history) - 1, 0, max(self.history)])
        plt.xlabel('Time (hours)')
        plt.ylabel('Value (Discoins)')
        plt.title(f'Stock Value Over Time: {self.name}')
        plt.legend()
        plt.grid(True)
        
        # Save the plot to a BytesIO object
        buf = io.BytesIO()
        plt.savefig(buf, format='png')
        plt.close()
        buf.seek(0)
        
        return buf