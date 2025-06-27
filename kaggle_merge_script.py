import pandas as pd
import ast
import csv
import os

# ✅ Step 1: Validate CSV Files Existence and Format
required_files = ['movies.csv', 'credits.csv']
for file in required_files:
    if not os.path.exists(file):
        raise FileNotFoundError(f"❌ Required file '{file}' not found in the current directory.")

# Quick check for file structure
try:
    test_movies = pd.read_csv('movies.csv', nrows=5)
    test_credits = pd.read_csv('credits.csv', nrows=5)
    print("✅ CSV files detected and format appears valid.")
except Exception as e:
    raise ValueError(f"❌ Error reading CSV files: {e}")

# 🛠️ Step 2: Load and Process the Dataset
movies = pd.read_csv('movies.csv', low_memory=False)
credits = pd.read_csv('credits.csv')

# Normalize and merge
movies['id'] = pd.to_numeric(movies['id'], errors='coerce')
credits['id'] = pd.to_numeric(credits['id'], errors='coerce')
movies = movies.dropna(subset=['id'])
credits = credits.dropna(subset=['id'])
movies['id'] = movies['id'].astype(int)
credits['id'] = credits['id'].astype(int)
movies = movies.merge(credits, on='id')

movies = movies.dropna(subset=['title', 'overview', 'genres', 'release_date'])
movies['year'] = pd.to_datetime(movies['release_date'], errors='coerce').dt.year

# Parse fields
def parse_genres(x):
    try:
        return ", ".join([d['name'] for d in ast.literal_eval(x)])
    except:
        return ""

def parse_crew(x):
    try:
        crew = ast.literal_eval(x)
        directors = [d['name'] for d in crew if d['job'] == 'Director']
        return ", ".join(directors)
    except:
        return ""

def parse_cast(x):
    try:
        cast = ast.literal_eval(x)
        return ", ".join([d['name'] for d in cast[:3]])
    except:
        return ""

movies['genres'] = movies['genres'].apply(parse_genres)
movies['director'] = movies['crew'].apply(parse_crew)
movies['stars'] = movies['cast'].apply(parse_cast)
movies['rating'] = movies['vote_average']
movies['description'] = movies['overview']




# Filter + Clean
final_df = movies[['id','title', 'genres', 'year', 'rating', 'description', 'director', 'stars']]
final_df = final_df.dropna(subset=['title', 'genres', 'rating']).copy()
final_df = final_df.drop_duplicates(subset='title', keep='first').copy()

columns_to_clean = ['title', 'genres', 'description', 'director', 'stars']
for col in columns_to_clean:
    final_df[col] = final_df[col].astype(str) \
        .str.replace('\n', ' ', regex=True) \
        .str.replace('\r', ' ', regex=True) \
        .str.replace('"', "'", regex=True)

# ✅ Step 3: Validate dataset before saving
print("🔍 Validating final DataFrame structure before saving...")
bad_rows = final_df[final_df.isnull().any(axis=1)]
if len(bad_rows) > 0:
    print(f"❌ Found {len(bad_rows)} rows with null values:")
    print(bad_rows.head())
    final_df = final_df.dropna()

print("🧪 Columns in final DataFrame:", final_df.columns.tolist())
print("🆔 Sample IDs:", final_df['id'].head())


# ✅ Step 4: Save CSV initially (preliminary version)
temp_path = 'combined_movies_temp.csv'
final_df.to_csv(
    temp_path,
    index=False,
    quoting=csv.QUOTE_ALL,
    quotechar='"',
    escapechar='\\',
    lineterminator='\n'
)

# ✅ Step 5: Validate and clean malformed rows (expecting exactly 7 columns)
valid_rows = []
with open(temp_path, 'r', encoding='utf-8') as infile:
    reader = csv.reader(infile, quotechar='"', escapechar='\\')
    headers = next(reader)
    for row in reader:
        if len(row) == 7:
            valid_rows.append(row)

# ✅ Step 6: Save cleaned version
final_csv_path = 'combined_movies.csv'
with open(final_csv_path, 'w', newline='', encoding='utf-8') as outfile:
    writer = csv.writer(outfile, quoting=csv.QUOTE_ALL, quotechar='"', escapechar='\\')
    writer.writerow(headers)
    writer.writerows(valid_rows)

# ✅ Final message
print(f"✅ Cleaned dataset saved as {final_csv_path} with {len(valid_rows)} valid rows.")