import pandas as pd
df = pd.read_csv("de_movies.csv")
print(df.head())

print("\nChecking for missing values:")
print(df.isnull().sum())

print("\nChecking for empty strings in important columns:")
columns_to_check = ["Title", "Rating", "Year", "Duration", "Genres", "Director", "Stars"]
for col in columns_to_check:
    empty = df[col].astype(str).str.strip() == ''
    print(f"{col}: {empty.sum()} empty entries")

df["Rating"] = pd.to_numeric(df["Rating"], errors="coerce")  # converts bad data to NaN

print("\nRatings not between 0 and 10:")
bad_ratings = df[(df["Rating"] < 0) | (df["Rating"] > 10)]
print(bad_ratings[["Title", "Rating"]])

# Step 1: Convert to string before using .str.extract()
df["Year"] = df["Year"].astype(str).str.extract(r'(\d{4})')  # Extract 4-digit year

# Step 2: Convert to numeric (invalid ones become NaN)
df["Year"] = pd.to_numeric(df["Year"], errors="coerce")

# Step 3: Check for invalid year ranges
print("\nInvalid Years (outside 1900–2025):")
bad_years = df[(df["Year"] < 1900) | (df["Year"] > 2025)]
print(bad_years[["Title", "Year"]])

# Fill missing optional fields
df["Director"] = df["Director"].fillna("Unknown")
df["Stars"] = df["Stars"].fillna("Unknown")

# Remove only rows with critical missing data
df_cleaned = df.dropna(subset=["Title", "Rating", "Year"])

# Keep valid ranges
df_cleaned = df_cleaned[(df_cleaned["Rating"] >= 0) & (df_cleaned["Rating"] <= 10)]
df_cleaned = df_cleaned[(df_cleaned["Year"] >= 1900) & (df_cleaned["Year"] <= 2025)]

# Save
df_cleaned.to_csv("de_movies_cleaned.csv", index=False)
print("\n✅ Cleaned data saved to 'de_movies_cleaned.csv'")

# upload data
from sqlalchemy import create_engine
import pandas as pd

# Load your cleaned CSV
df = pd.read_csv("de_movies_cleaned.csv")

# Connect to the database
engine = create_engine("postgresql+psycopg2://postgres:postgres@localhost:5432/imdb_movies")

df.columns = [col.split('__')[0].lower() for col in df.columns]


print("🧾 Columns being uploaded:", df.columns.tolist())



# Upload the data
df.to_sql('movies', con=engine, index=False, if_exists='append')

print("✅ Data uploaded successfully!")

