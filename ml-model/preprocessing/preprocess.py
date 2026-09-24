import pandas as pd
import re


def clean_text(text):
    if pd.isna(text):
        return ""

    text = text.lower()
    text = re.sub(r"[^a-z0-9| ]", " ", text)
    text = re.sub(r"\s+", " ", text)

    return text.strip()


def load_and_prepare_movies():
    movies = pd.read_csv("../dataset/movies.csv")

    movies["genres"] = movies["genres"].fillna("")
    movies["title"] = movies["title"].fillna("")

    movies["content"] = (
        movies["title"].apply(clean_text)
        + " "
        + movies["genres"].apply(clean_text)
    )

    return movies


if __name__ == "__main__":
    movies = load_and_prepare_movies()

    print("Movies loaded:", len(movies))
    print("\nSample data:")
    print(movies[["movieId", "title", "genres", "content"]].head())