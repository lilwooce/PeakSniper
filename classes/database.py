import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from Base import Base

load_dotenv()

# Import all classes
from classes import Servers, User

# Create database structure
host = os.getenv("host")
user = os.getenv("user")
pwd = os.getenv("password")
database = os.getenv("database")
port = os.getenv("port")
# engine = create_engine(f"mysql+pymysql://{user}:{pwd}@{host}/{database}", isolation_level="READ COMMITTED") # Use for MariaDB
print(f"user: {user}, pwd: {pwd}, host: {host}, port: {port}, database: {database}")
engine = create_engine(f"mysql+mysqlconnector://{user}:{pwd}@{host}:{port}/{database}", pool_pre_ping=True, isolation_level="READ COMMITTED") # Use for MySQL
Base.metadata.create_all(engine)