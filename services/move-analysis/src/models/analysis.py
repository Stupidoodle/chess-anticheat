from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, DateTime, Float
from datetime import datetime

Base = declarative_base()


class MoveAnalysis(Base):
    __tablename__ = "move_analyses"

    id = Column(String, primary_key=True)
    game_id = Column(String, index=True)
    move_number = Column(Integer)
    position_fen = Column(String)
    move_uci = Column(String)
    time_taken = Column(Float)
    complexity_score = Column(Float)
    engine_correlation = Column(Float)
