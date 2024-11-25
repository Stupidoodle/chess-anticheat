from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, DateTime, Float
from datetime import datetime

Base = declarative_base()


class GameBase(Base):
    __tablename__ = "games"

    id = Column(String, primary_key=True)
    white_player_id = Column(String, index=True)
    black_player_id = Column(String, index=True)
    start_time = Column(DateTime, default=datetime.utcnow)
    time_control = Column(String)
    status = Column(String)
