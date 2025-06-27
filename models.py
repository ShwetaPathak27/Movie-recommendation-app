# models.py
from sqlalchemy import Column, Integer, Float, String, Text
from database import Base

# 🎬 IMDb Movie Table
class IMDbMovie(Base):
    __tablename__ = "movies"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    title = Column(String)
    genres = Column(String)
    year = Column(Integer)
    rating = Column(Float)
    description = Column(Text)
    director = Column(String)
    stars = Column(String)

# 🎬 Kaggle Movie Table
class KaggleMovie(Base):
    __tablename__ = "movies_combined"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    title = Column(String)
    genres = Column(String)
    year = Column(Integer)
    rating = Column(Float)
    description = Column(Text)
    director = Column(String)
    stars = Column(String)
