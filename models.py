from sqlalchemy import Column, Integer, String, ForeignKey
from database import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True)
    password = Column(String)
    score = Column(Integer, default=0)
    wins = Column(Integer, default=0)

class Game(Base):
    __tablename__ = "games"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    game_type = Column(String)
    secret = Column(String)
    attempts = Column(Integer, default=0)
    lives = Column(Integer)
    status = Column(String, default="active")