from sqlalchemy import Column, String, Integer, BigInteger
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Asset(Base):
    __tablename__ = "Assets"

    id = Column("id", Integer, primary_key=True)
    name = Column("name", String(80))
    material = Column("material", String(80))
    purchase_value = Column("purchase_value", BigInteger)
    current_value = Column("current_value", BigInteger)
    type_of = Column("type_of", String(80))
    owner = Column("owner", BigInteger)

    def __init__(self, name, material, purchase_value, type_of):
        self.name = name
        self.material = material
        self.purchase_value = purchase_value
        self.current_value = purchase_value
        self.type_of = type_of
        self.owner = 0
