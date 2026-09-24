import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


class MovieRecommender:

    def __init__(self, dataset_path="dataset/movies.csv"):
        self.movies = pd.read_csv(dataset_path)

        self.movies["genres"] = self.movies["genres"].fillna("")
        self.movies["title"] = self.movies["title"].fillna("")

        self.movies["content"] = (
            self.movies["title"]
            + " "
            + self.movies["genres"]
        )

        # Convert movie content into numerical vectors
        self.vectorizer = TfidfVectorizer(
            stop_words="english"
        )

        self.movie_vectors = self.vectorizer.fit_transform(
            self.movies["content"]
        )

        # Calculate similarity between movies
        self.similarity_matrix = cosine_similarity(
            self.movie_vectors
        )

        # Movie title → index
        self.movie_indices = pd.Series(
            self.movies.index,
            index=self.movies["title"]
        ).drop_duplicates()

    def recommend(self, movie_title, number_of_recommendations=10):

        if movie_title not in self.movie_indices:
            return []

        movie_index = self.movie_indices[movie_title]

        similarity_scores = list(
            enumerate(self.similarity_matrix[movie_index])
        )

        similarity_scores = sorted(
            similarity_scores,
            key=lambda x: x[1],
            reverse=True
        )

        # Remove the selected movie itself
        similarity_scores = similarity_scores[1:]

        recommendations = []

        for index, score in similarity_scores[
            :number_of_recommendations
        ]:
            recommendations.append({
                "movieId": int(self.movies.iloc[index]["movieId"]),
                "title": self.movies.iloc[index]["title"],
                "genres": self.movies.iloc[index]["genres"],
                "similarity_score": round(float(score), 4)
            })

        return recommendations


if __name__ == "__main__":

    recommender = MovieRecommender()

    movie = "Toy Story (1995)"

    recommendations = recommender.recommend(movie, 10)

    print(f"\nRecommendations for: {movie}\n")

    for item in recommendations:
        print(
            f"{item['title']} "
            f"| {item['genres']} "
            f"| Score: {item['similarity_score']}"
        )