import json
import random
from sqlalchemy import Column, String, Integer, Boolean, Text, BigInteger, TIMESTAMP
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

default_prefix = "."

class Servers(Base):
    __tablename__ = "Servers"

    id = Column("id", Integer, primary_key=True)
    server_id = Column("server_id", BigInteger)
    name = Column("name", String(80))
    prefix = Column("prefix", String(80))
    currently_in_server = Column("currently_in_server", Boolean)

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



    def __init__(self, server):
        self.server_id = server.id
        self.name = server.name
        self.prefix = default_prefix
        self.currently_in_server = True
        self.recently_deleted_message = ""
        self.recently_deleted_images = ""
        self.recently_deleted_timestamp = ""
        self.recently_deleted_user = 0
        self.recently_deleted_reply = ""
        self.recently_edited_user = 0
        self.recently_edited_timestamp = ""
        self.recently_edited_images = ""
        self.recently_edited_before_message = ""
        self.recently_edited_after_message = ""
        self.recently_edited_reply = ""
    
    def change_deleted():
        return

    def change_edited():
        return
