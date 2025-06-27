import pandas as pd
import sys
from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError

# Step 1: Determine source
source = sys.argv[1] if len(sys.argv) > 1 else "kaggle"  # default to kaggle

if source not in ["imdb", "kaggle"]:
    raise ValueError("❌ Source must be 'imdb' or 'kaggle'")

# Step 2: File and table based on source
if source == "imdb":
    csv_file = "imdb_movies_clean.csv"
    table_name = "imdb_movies"
elif source == "kaggle":
    csv_file = "combined_movies_temp.csv"
    table_name = "movies_combined"

# Step 3: Load CSV
try:
    df = pd.read_csv(csv_file)
except Exception as e:
    print(f"❌ Error reading CSV file: {e}")
    sys.exit(1)

# Step 4: Clean DataFrame
required_columns = ["title", "genres", "year", "rating", "description", "director", "stars"]
for col in ["genres", "stars", "director", "description"]:
    df[col] = df[col].fillna("Unknown")

df["year"] = pd.to_numeric(df["year"], errors="coerce")
df["rating"] = pd.to_numeric(df["rating"], errors="coerce")
df = df.dropna(subset=["title", "genres", "rating", "year"])
df = df[required_columns]

# Step 5: Upload to PostgreSQL
try:
    engine = create_engine("postgresql+psycopg2://postgres:postgres@localhost:5432/imdb_movies")
    df.to_sql(table_name, engine, if_exists="append", index=False)
    print(f"✅ Uploaded {len(df)} rows to '{table_name}' successfully.")
except SQLAlchemyError as e:
    print(f"❌ Database upload failed: {e}")
