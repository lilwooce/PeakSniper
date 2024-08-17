import json
import random
from sqlalchemy import Column, String, Integer, Boolean, Text, BigInteger
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

default_prefix = "."

class Servers(Base):
    __tablename__ = "Servers"

    id = Column("id", Integer, primary_key=True)
    server_id = ("server_id", BigInteger)
    name = Column("name", String(80))
    prefix = Column("prefix", String(80))
    recently_deleted = Column("recently_deleted", String(2000))
    recently_edited = Column("recently_edited", String(2000))
    currently_in_server = Column("currently_in_server", Boolean)



    def __init__(self, server):
        self.name = server.name
        self.server_id = server.id
        self.prefix = default_prefix
        self.recently_deleted = ""
        self.recently_edited = ""
        self.currently_in_server = True
    
    def change_deleted():
        return

    def change_edited():
        return
