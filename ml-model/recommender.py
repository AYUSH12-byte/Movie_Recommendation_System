import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


class MovieRecommender:

    def __init__(self, dataset_path="dataset/movies.csv"):

        print("Loading movie dataset...")

        self.movies = pd.read_csv(dataset_path)

        self.movies["genres"] = self.movies["genres"].fillna("")
        self.movies["title"] = self.movies["title"].fillna("")

        # Combine title and genres
        self.movies["content"] = (
            self.movies["title"] + " " + self.movies["genres"]
        )

        print("Creating TF-IDF vectors...")

        self.vectorizer = TfidfVectorizer(
            stop_words="english"
        )

        self.movie_vectors = self.vectorizer.fit_transform(
            self.movies["content"]
        )

        # Movie title -> dataframe index
        self.movie_indices = pd.Series(
            self.movies.index,
            index=self.movies["title"]
        ).drop_duplicates()

        print("Recommendation engine ready!")


    def recommend(self, movie_title, number_of_recommendations=10):

        if movie_title not in self.movie_indices:
            print(f"Movie not found: {movie_title}")
            return []

        movie_index = self.movie_indices[movie_title]

        # Calculate similarity ONLY for selected movie
        movie_vector = self.movie_vectors[movie_index]

        similarity_scores = cosine_similarity(
            movie_vector,
            self.movie_vectors
        ).flatten()

        # Get highest similarity indexes
        similar_indexes = similarity_scores.argsort()[
            ::-1
        ][1:number_of_recommendations + 1]

        recommendations = []

        for index in similar_indexes:

            recommendations.append({
                "movieId": int(
                    self.movies.iloc[index]["movieId"]
                ),
                "title": self.movies.iloc[index]["title"],
                "genres": self.movies.iloc[index]["genres"],
                "similarity_score": round(
                    float(similarity_scores[index]),
                    4
                )
            })

        return recommendations


if __name__ == "__main__":

    recommender = MovieRecommender()

    movie = "Toy Story (1995)"

    recommendations = recommender.recommend(
        movie,
        10
    )

    print(
        f"\nRecommendations for: {movie}\n"
    )

    for item in recommendations:

        print(
            f"{item['title']} "
            f"| {item['genres']} "
            f"| Score: {item['similarity_score']}"
        )