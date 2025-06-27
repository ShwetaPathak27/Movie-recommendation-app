from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional, Union
from database import get_db
import crud
import re
from recommender import load_combined_data, get_combined_recommendations
from schemas import IMDbMovieOut, KaggleMovieOut

router = APIRouter()

# 🎯 Combined response model union
MovieResponseModel = Union[IMDbMovieOut, KaggleMovieOut]

@router.get("/recommendations/filter", response_model=List[MovieResponseModel])
def filtered_recommendations(
    title: Optional[str] = None,
    genre: Optional[str] = None,
    rating: Optional[float] = None,
    db: Session = Depends(get_db)
):
    if not any([title, genre, rating]):
        raise HTTPException(status_code=400, detail="⚠️ Provide at least one filter (title, genre, or rating).")

    if re.search(r"[^a-zA-Z0-9\s]", title or "") or re.search(r"[^a-zA-Z0-9\s]", genre or ""):
        raise HTTPException(status_code=400, detail="❌ Invalid characters in title or genre.")

    imdb_movies = crud.get_imdb_movies(db)
    kaggle_movies = crud.get_kaggle_movies(db)

    # Load into FAISS-based recommender
    from recommender import load_combined_data, get_combined_recommendations
    load_combined_data(imdb_movies, kaggle_movies)

    recommendations = get_combined_recommendations(title=title, genre=genre, rating=rating, top_n=5)

    if title:
        all_titles = [m.title.lower().strip() for m in imdb_movies + kaggle_movies]
        if title.lower().strip() not in all_titles:
            raise HTTPException(status_code=404, detail="❌ Title not found in either dataset.")

    if not recommendations:
        raise HTTPException(status_code=404, detail="😢 No movies found for your filters.")

    return recommendations


@router.get("/search", response_model=List[MovieResponseModel])
def search_movies(
    query: str = Query(..., min_length=1, description="Movie title to search"),
    db: Session = Depends(get_db)
):
    if re.search(r"[^a-zA-Z0-9\s]", query):
        raise HTTPException(status_code=400, detail="❌ Only letters, digits, and spaces allowed.")

    imdb_movies = crud.get_imdb_movies(db)
    kaggle_movies = crud.get_kaggle_movies(db)
    all_movies = imdb_movies + kaggle_movies

    results = [m for m in all_movies if query.lower().strip() in m.title.lower().strip()]

    if not results:
        raise HTTPException(status_code=404, detail="😢 No matching movies found.")

    return results
