from sqlalchemy import Column,Integer,String,Float
from database import Base


class Food(Base):
    __tablename__ = "food"
    id = Column(Integer,primary_key=True,index=True)
    name = Column(String(100),unique=True,nullable=False)
    calories_per_100g=Column(Float,nullable=False)
