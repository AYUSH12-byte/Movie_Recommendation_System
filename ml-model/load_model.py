import pickle


def load_recommender(
    model_path="models/movie_recommender.pkl"
):

    with open(model_path, "rb") as file:
        model = pickle.load(file)

    return model


if __name__ == "__main__":

    model = load_recommender()

    print(
        "Model loaded successfully!"
    )

    print(
        "Total movies:",
        len(model["movies"])
    )