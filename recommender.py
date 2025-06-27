import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
import faiss
import numpy as np

# Global variables
combined_df = None
faiss_index = None
vector_matrix = None


def load_combined_data(imdb_movies, kaggle_movies):
    """
    Merge IMDb and Kaggle movies, vectorize with TF-IDF, and build FAISS index.
    """
    global combined_df, faiss_index, vector_matrix

    def to_df(movies, source):
        return pd.DataFrame([{
            "id": m.id,
            "title": m.title or "",
            "year": str(m.year) if m.year else "",
            "rating": float(m.rating) if str(m.rating).strip() not in ["", "None"] else None,
            "genres": m.genres or "",
            "director": m.director or "",
            "stars": m.stars or "",
            "description": m.description or "",
            "source": source
        } for m in movies])

    imdb_df = to_df(imdb_movies, "imdb")
    kaggle_df = to_df(kaggle_movies, "kaggle")
    combined_df = pd.concat([imdb_df, kaggle_df], ignore_index=True)

    # Prepare content
    combined_df["content"] = (
    (combined_df["title"] + " ") * 3 +
    (combined_df["genres"] + " ") * 2 +
    (combined_df["director"] + " ") * 2 +
    (combined_df["stars"] + " ") * 2 +
    (combined_df["description"] + " ") * 2
).str.lower().fillna("")

    vectorizer = TfidfVectorizer(stop_words="english", max_features=10000)
    tfidf_matrix = vectorizer.fit_transform(combined_df["content"])
    vector_matrix = tfidf_matrix.astype(np.float32).toarray()

    # Normalize and build FAISS index
    faiss.normalize_L2(vector_matrix)
    faiss_index = faiss.IndexFlatIP(vector_matrix.shape[1])
    faiss_index.add(vector_matrix)


def get_combined_recommendations(title: str = "", genre: str = "", rating: float = None, top_n: int = 10):
    """
    Recommend top N similar movies using FAISS with fallback strategy.
    """
    global combined_df, faiss_index, vector_matrix

    if combined_df is None or faiss_index is None:
        print("❌ Data or FAISS index not loaded.")
        return []

    filtered_df = combined_df.copy()

    # Apply genre filter
    if genre:
        filtered_df = filtered_df[filtered_df["genres"].str.lower().str.contains(genre.lower(), na=False)]

    # Apply rating filter
    if rating is not None:
        filtered_df["rating"] = pd.to_numeric(filtered_df["rating"], errors="coerce")
        filtered_df = filtered_df[filtered_df["rating"].notna()]
        filtered_df = filtered_df[filtered_df["rating"] >= float(rating)]

    print("🧾 Filtered count:", len(filtered_df))
    print("🧾 Filtered titles:", filtered_df["title"].tolist())

    if title:
        clean_title = title.strip().lower()
        idx_list = combined_df[combined_df["title"].str.lower().str.strip() == clean_title].index
        if idx_list.empty:
            print("❌ Title not found in dataset.")
            return []

        query_idx = idx_list[0]
        query_vector = vector_matrix[query_idx].reshape(1, -1)
        D, I = faiss_index.search(query_vector, top_n + 10)  # Search wider for better fallback room

        recommendations = []
        seen = set()
        for i in I[0]:
            if i == query_idx or i in seen:
                continue
            if i in filtered_df.index:
                recommendations.append(combined_df.iloc[i])
                seen.add(i)
            if len(recommendations) >= top_n:
                break

        # 🛟 Fallback: if not enough results, drop filters progressively
        if len(recommendations) < top_n:
            print("⚠️ Not enough filtered results. Applying fallback without rating filter.")
            fallback_df = combined_df.copy()

            if genre:
                fallback_df = fallback_df[fallback_df["genres"].str.lower().str.contains(genre.lower(), na=False)]

            for i in I[0]:
                if i == query_idx or i in seen:
                    continue
                if i in fallback_df.index:
                    recommendations.append(combined_df.iloc[i])
                    seen.add(i)
                if len(recommendations) >= top_n:
                    break

        return [r.to_dict() for r in recommendations]

    # 🔄 No title provided, fallback to genre/rating filters
    if filtered_df.empty:
        print("⚠️ No matches found after filters. Falling back to genre only.")
        fallback_df = combined_df.copy()
        if genre:
            fallback_df = fallback_df[fallback_df["genres"].str.lower().str.contains(genre.lower(), na=False)]
        return fallback_df.head(top_n).to_dict(orient="records")

    return filtered_df.head(top_n).to_dict(orient="records")
