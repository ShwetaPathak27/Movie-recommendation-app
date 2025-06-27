from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

import models
import routes
from database import engine

# ✅ Step 1: Create tables based on models if they don’t exist
models.Base.metadata.create_all(bind=engine)

# ✅ Step 2: Initialize FastAPI app
app = FastAPI(
    title="Movie Recommendation System",
    description="API for searching, filtering and recommending movies from PostgreSQL",
    version="1.0.0"
)

# ✅ Step 3: CORS Configuration (adjust frontend URL if needed)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:5500"],  # Update if you're using a different frontend port
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ Step 4: Register routes from `routes.py`
app.include_router(routes.router)

# ✅ Optional Root Route
@app.get("/")
def read_root():
    return {"message": "🎬 Welcome to the Movie Recommendation API"}

