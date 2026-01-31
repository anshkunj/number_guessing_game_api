from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    password = Column(String)

    score = Column(Integer, default=0)
    wins = Column(Integer, default=0)


class Game(Base):
    __tablename__ = "games"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    game_type = Column(String)
    secret = Column(String)
    lives = Column(Integer)
    attempts = Column(Integer)
    status = Column(String)


class Chat(Base):
    __tablename__ = "chat"

    id = Column(Integer, primary_key=True)
    username = Column(String)
    message = Column(String)