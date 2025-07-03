import pandas as pd
import numpy as np
import ast
import pickle
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import os

print(" Script started...")

# Load datasets
movies = pd.read_csv('tmdb_5000_movies.csv')
credits = pd.read_csv('tmdb_5000_credits.csv')

# Merge on title
movies = movies.merge(credits, on='title')

# Keep necessary columns
movies = movies[['movie_id', 'title', 'overview', 'genres', 'keywords', 'cast', 'crew']]

# Helper functions
def convert(obj):
    try:
        return [i['name'] for i in ast.literal_eval(obj)]
    except:
        return []

def get_director(obj):
    try:
        for i in ast.literal_eval(obj):
            if i['job'] == 'Director':
                return i['name']
    except:
        return ''

def collapse(l):
    return [i.replace(" ", "") for i in l]

# Apply transformations
movies.dropna(inplace=True)
movies['genres'] = movies['genres'].apply(convert)
movies['keywords'] = movies['keywords'].apply(convert)
movies['cast'] = movies['cast'].apply(lambda x: convert(x)[:3])  # top 3 cast members
movies['crew'] = movies['crew'].apply(get_director)
movies['overview'] = movies['overview'].apply(lambda x: x.split())
movies['genres'] = movies['genres'].apply(collapse)
movies['keywords'] = movies['keywords'].apply(collapse)
movies['cast'] = movies['cast'].apply(collapse)
movies['crew'] = movies['crew'].apply(lambda x: x.replace(" ", "") if isinstance(x, str) else "")


# Create 'tags' feature
movies['tags'] = movies['overview'] + movies['genres'] + movies['keywords'] + movies['cast'] + movies['crew'].apply(lambda x: [x])

# New dataframe
new = movies[['movie_id', 'title', 'tags']]
new['tags'] = new['tags'].apply(lambda x: " ".join(x))
new['tags'] = new['tags'].apply(lambda x: x.lower())

# Vectorization
cv = CountVectorizer(max_features=5000, stop_words='english')
vectors = cv.fit_transform(new['tags']).toarray()

# Similarity matrix
similarity = cosine_similarity(vectors)

# Save files to fixed paths
dict_path = r'C:\Movie-Recommendation-System\movies_dict.pkl'
sim_path = r'C:\Movie-Recommendation-System\similarity.pkl'

try:
    with open(dict_path, 'wb') as f:
        pickle.dump(new.to_dict(), f)
    print(f" Saved movies_dict.pkl at: {dict_path}")
except Exception as e:
    print(f"❌ Failed to save movies_dict.pkl: {e}")

try:
    with open(sim_path, 'wb') as f:
        pickle.dump(similarity, f)
    print(f" Saved similarity.pkl at: {sim_path}")
except Exception as e:
    print(f" Failed to save similarity.pkl: {e}")
