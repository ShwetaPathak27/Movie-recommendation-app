from sqlalchemy.orm import Session
from datetime import timedelta
from typing import Type, List
from models import IMDbMovie, KaggleMovie


def get_imdb_movies(
    db: Session,
    search: str = "",
    sort_by: str = "title",
    skip: int = 0,
    limit: int = 50000
) -> List[IMDbMovie]:
    return _get_movies(db, IMDbMovie, search, sort_by, skip, limit)


def get_kaggle_movies(
    db: Session,
    search: str = "",
    sort_by: str = "title",
    skip: int = 0,
    limit: int = 50000
) -> List[KaggleMovie]:
    return _get_movies(db, KaggleMovie, search, sort_by, skip, limit)


# 🔧 Shared logic for both IMDb and Kaggle tables
def _get_movies(
    db: Session,
    model: Type,
    search: str,
    sort_by: str,
    skip: int,
    limit: int
):
    query = db.query(model)

    # 🔍 Filter by search
    if search:
        query = query.filter(model.title.ilike(f"%{search}%"))

    # 🧠 Supported sort fields
    sort_fields = {
        "title": model.title,
        "year": model.year,
        "rating": model.rating,
        "genres": model.genres,
        "director": model.director,
        "stars": model.stars,
        "description": model.description,
    }
    sort_column = sort_fields.get(sort_by, model.title)
    query = query.order_by(sort_column)

    # 📦 Pagination
    movies = query.offset(skip).limit(limit).all()

    # ⏱️ Format duration
    for movie in movies:
        if hasattr(movie, "duration"):
            if isinstance(movie.duration, timedelta):
                total_minutes = int(movie.duration.total_seconds() // 60)
                hours = total_minutes // 60
                minutes = total_minutes % 60
                movie.duration = f"{hours}h {minutes}m"
            elif isinstance(movie.duration, str):
                movie.duration = movie.duration.strip()

    return movies
