import json
import random
from sqlalchemy import Column, String, Integer, Boolean, Text, BigInteger, TIMESTAMP
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

default_prefix = "."

class Servers(Base):
    __tablename__ = "Servers"

    id = Column("id", Integer, primary_key=True)
    server_id = ("server_id", BigInteger)
    name = Column("name", String(80))
    prefix = Column("prefix", String(80))
    recently_deleted_message = Column("recently_deleted_message", String(2000))
    recently_deleted_images = Column("recently_deleted_images", String(2000))
    recently_deleted_timestamp = Column("recently_deleted_timestamp", TIMESTAMP)
    recently_deleted_user = Column("recently_deleted_user", BigInteger)
    recently_deleted_reply = Column("recently_deleted_reply", String(2000))

    recently_edited_user = Column("recently_edited_user", BigInteger)
    recently_edited_timestamp = Column("recently_edited_timestamp", TIMESTAMP)
    recently_edited_images = Column("recently_edited_images", String(2000))
    recently_edited_before_message = Column("recently_edited_before_message", String(2000))
    recently_edited_after_message = Column("recently_edited_after_message", String(2000))
    recently_edited_reply = Column("recently_edited_reply", String(2000))

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
