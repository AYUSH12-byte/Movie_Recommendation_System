import pandas as pd

movies = pd.read_csv("dataset/movies.csv")
ratings = pd.read_csv("dataset/ratings.csv")

print("Movies:")
print(movies.head())

print("\nRatings:")
print(ratings.head())

print("\nMovie count:", len(movies))
print("Rating count:", len(ratings))
print("User count:", ratings["userId"].nunique())