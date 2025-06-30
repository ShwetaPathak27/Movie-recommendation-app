from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

import models
import routes
from database import engine

# Create tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Movie Recommendation System",
    description="API for searching, filtering and recommending movies from PostgreSQL",
    version="1.0.0"
)

# Serve static files (e.g. JS, CSS, images if needed)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Serve the main index.html
@app.get("/", response_class=FileResponse)
def read_index():
    return "static/index.html"

# CORS config — now optional, but keep it open if needed
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all for testing; restrict later if deployed
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API routes
app.include_router(routes.router)
