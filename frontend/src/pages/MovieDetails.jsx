import { useEffect, useState } from "react";
import {
  Link,
  useNavigate,
  useParams,
} from "react-router-dom";

import api from "../services/api";
import { useAuth } from "../context/AuthContext";

function MovieDetails() {
  const { movieId } = useParams();
  const navigate = useNavigate();

  const {
    user,
    isAuthenticated,
  } = useAuth();

  const [movie, setMovie] = useState(null);
  const [userRating, setUserRating] = useState(null);
  const [selectedRating, setSelectedRating] = useState(0);

  const [loading, setLoading] = useState(true);
  const [ratingLoading, setRatingLoading] = useState(false);

  const [error, setError] = useState("");
  const [ratingMessage, setRatingMessage] = useState("");


  // ==========================================================
  // FETCH MOVIE
  // ==========================================================

  useEffect(() => {
    const fetchMovie = async () => {
      try {
        setLoading(true);
        setError("");

        const response = await api.get(
          `/movies/${movieId}`
        );

        console.log(
          "MOVIE DETAILS RESPONSE:",
          response.data
        );

        setMovie(
          response.data.movie
        );

      } catch (err) {
        console.error(
          "Failed to fetch movie:",
          err
        );

        setError(
          err.response?.data?.detail ||
          "Failed to load movie details."
        );
      } finally {
        setLoading(false);
      }
    };

    fetchMovie();
  }, [movieId]);


  // ==========================================================
  // FETCH USER RATING
  // ==========================================================

  useEffect(() => {
    if (!isAuthenticated) {
      return;
    }

    const fetchUserRating = async () => {
      try {
        const response = await api.get(
          `/ratings/movie/${movieId}`
        );

        console.log(
          "USER RATING:",
          response.data
        );

        const rating =
          response.data.rating ??
          response.data.userRating ??
          null;

        setUserRating(rating);

        if (rating) {
          setSelectedRating(
            Number(rating)
          );
        }

      } catch (err) {
        console.log(
          "No existing user rating.",
          err.response?.data
        );
      }
    };

    fetchUserRating();

  }, [
    movieId,
    isAuthenticated
  ]);


  // ==========================================================
  // SUBMIT RATING
  // ==========================================================

  const handleRating = async () => {
    if (!isAuthenticated) {
      navigate("/login");
      return;
    }

    if (!selectedRating) {
      setRatingMessage(
        "Please select a rating first."
      );
      return;
    }

    try {
      setRatingLoading(true);
      setRatingMessage("");

      const response = await api.post(
        "/ratings/",
        {
          movieId: Number(movieId),
          rating: Number(selectedRating),
        }
      );

      console.log(
        "RATING RESPONSE:",
        response.data
      );

      setUserRating(
        Number(selectedRating)
      );

      setRatingMessage(
        "Your rating has been saved successfully."
      );

    } catch (err) {
      console.error(
        "Failed to submit rating:",
        err
      );

      setRatingMessage(
        err.response?.data?.detail ||
        "Failed to save your rating."
      );

    } finally {
      setRatingLoading(false);
    }
  };


  // ==========================================================
  // LOADING
  // ==========================================================

  if (loading) {
    return (
      <div className="min-h-screen bg-slate-950 text-white">

        <div className="mx-auto max-w-7xl px-6 py-10">

          <div className="animate-pulse">

            <div className="mb-8 h-6 w-32 rounded bg-slate-800" />

            <div className="grid gap-10 md:grid-cols-[280px_1fr]">

              <div className="aspect-[2/3] rounded-2xl bg-slate-800" />

              <div className="space-y-5">

                <div className="h-10 w-2/3 rounded bg-slate-800" />

                <div className="h-5 w-1/3 rounded bg-slate-800" />

                <div className="h-24 rounded bg-slate-800" />

              </div>

            </div>

          </div>

        </div>

      </div>
    );
  }


  // ==========================================================
  // ERROR
  // ==========================================================

  if (error || !movie) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-slate-950 px-6 text-white">

        <div className="max-w-md text-center">

          <div className="mb-4 text-6xl">
            🎬
          </div>

          <h1 className="text-2xl font-bold">
            Movie Not Found
          </h1>

          <p className="mt-3 text-slate-400">
            {error ||
              "The requested movie could not be found."}
          </p>

          <Link
            to="/recommendations"
            className="mt-6 inline-flex rounded-lg bg-blue-600 px-5 py-3 font-semibold transition hover:bg-blue-500"
          >
            ← Back to Movies
          </Link>

        </div>

      </div>
    );
  }


  // ==========================================================
  // MOVIE DATA
  // ==========================================================

  const poster =
    movie.posterUrl ||
    movie.poster ||
    null;

  const backdrop =
    movie.backdropUrl ||
    null;

  const averageRating =
    movie.averageRating ??
    movie.communityRating ??
    null;

  const ratingCount =
    movie.totalRatings ??
    movie.ratingCount ??
    null;

  const tmdbRating =
    movie.tmdbRating ??
    null;

  const releaseDate =
    movie.releaseDate ||
    null;

  const genres =
    movie.genres
      ? movie.genres.split("|")
      : [];


  // ==========================================================
  // UI
  // ==========================================================

  return (
    <div className="min-h-screen bg-slate-950 text-white">

      {/* ================================================== */}
      {/* BACKDROP */}
      {/* ================================================== */}

      <section className="relative overflow-hidden">

        {backdrop && (
          <div className="absolute inset-0">

            <img
              src={backdrop}
              alt=""
              className="h-full w-full object-cover opacity-20"
            />

            <div className="absolute inset-0 bg-gradient-to-b from-slate-950/40 via-slate-950/80 to-slate-950" />

          </div>
        )}

        <div className="relative mx-auto max-w-7xl px-6 py-8">

          {/* Back Button */}

          <Link
            to="/recommendations"
            className="inline-flex items-center rounded-lg border border-slate-700 bg-slate-900/70 px-4 py-2 text-sm font-medium text-slate-200 backdrop-blur transition hover:border-blue-500 hover:text-blue-400"
          >
            ← Back to Movies
          </Link>


          {/* ================================================= */}
          {/* MOVIE CONTENT */}
          {/* ================================================= */}

          <div className="mt-10 grid gap-10 md:grid-cols-[280px_1fr]">

            {/* Poster */}

            <div className="overflow-hidden rounded-2xl border border-slate-800 bg-slate-900 shadow-2xl">

              {poster ? (
                <img
                  src={poster}
                  alt={movie.title}
                  className="h-full w-full object-cover"
                />
              ) : (
                <div className="flex aspect-[2/3] flex-col items-center justify-center gap-3 text-slate-500">

                  <span className="text-6xl">
                    🎬
                  </span>

                  <span>
                    No poster available
                  </span>

                </div>
              )}

            </div>


            {/* Movie Info */}

            <div className="flex flex-col justify-center">

              {/* Title */}

              <h1 className="text-4xl font-extrabold tracking-tight sm:text-5xl">

                {movie.title}

              </h1>


              {/* Genres */}

              {genres.length > 0 && (
                <div className="mt-5 flex flex-wrap gap-2">

                  {genres.map(
                    (genre) => (
                      <span
                        key={genre}
                        className="rounded-full border border-slate-700 bg-slate-900/80 px-3 py-1 text-sm text-slate-300"
                      >
                        {genre}
                      </span>
                    )
                  )}

                </div>
              )}


              {/* Ratings */}

              <div className="mt-6 flex flex-wrap gap-4">

                {averageRating !== null && (
                  <div className="rounded-xl border border-slate-800 bg-slate-900/80 px-4 py-3">

                    <div className="text-xs text-slate-500">
                      Community Rating
                    </div>

                    <div className="mt-1 text-lg font-bold">
                      ⭐{" "}
                      {Number(
                        averageRating
                      ).toFixed(1)}
                      /5
                    </div>

                  </div>
                )}


                {ratingCount !== null && (
                  <div className="rounded-xl border border-slate-800 bg-slate-900/80 px-4 py-3">

                    <div className="text-xs text-slate-500">
                      Ratings
                    </div>

                    <div className="mt-1 text-lg font-bold">
                      {ratingCount}
                    </div>

                  </div>
                )}


                {tmdbRating !== null && (
                  <div className="rounded-xl border border-slate-800 bg-slate-900/80 px-4 py-3">

                    <div className="text-xs text-slate-500">
                      TMDB Rating
                    </div>

                    <div className="mt-1 text-lg font-bold">
                      ⭐{" "}
                      {Number(
                        tmdbRating
                      ).toFixed(1)}
                    </div>

                  </div>
                )}

              </div>


              {/* Release Date */}

              {releaseDate && (
                <p className="mt-5 text-sm text-slate-400">

                  Release Date:{" "}

                  <span className="font-medium text-slate-200">
                    {releaseDate}
                  </span>

                </p>
              )}


              {/* Overview */}

              {movie.overview && (
                <div className="mt-7 max-w-3xl">

                  <h2 className="text-xl font-bold">
                    Overview
                  </h2>

                  <p className="mt-3 leading-7 text-slate-400">
                    {movie.overview}
                  </p>

                </div>
              )}

            </div>

          </div>

        </div>

      </section>


      {/* ================================================== */}
      {/* RATING SECTION */}
      {/* ================================================== */}

      <section className="mx-auto max-w-7xl px-6 pb-16">

        <div className="mt-8 max-w-2xl rounded-2xl border border-slate-800 bg-slate-900 p-6">

          <h2 className="text-xl font-bold">
            Rate this movie
          </h2>

          {isAuthenticated ? (
            <>
              <p className="mt-2 text-sm text-slate-400">
                {userRating
                  ? `Your current rating: ${userRating}/5`
                  : "How would you rate this movie?"}
              </p>


              {/* Stars */}

              <div className="mt-5 flex gap-2">

                {[1, 2, 3, 4, 5].map(
                  (star) => (
                    <button
                      key={star}
                      type="button"
                      onClick={() =>
                        setSelectedRating(
                          star
                        )
                      }
                      className={`text-4xl transition ${
                        star <=
                        selectedRating
                          ? "text-yellow-400"
                          : "text-slate-700"
                      } hover:scale-110`}
                    >
                      ★
                    </button>
                  )
                )}

              </div>


              {/* Submit */}

              <button
                type="button"
                onClick={handleRating}
                disabled={
                  ratingLoading ||
                  !selectedRating
                }
                className="mt-5 rounded-lg bg-blue-600 px-5 py-3 font-semibold transition hover:bg-blue-500 disabled:cursor-not-allowed disabled:opacity-50"
              >
                {ratingLoading
                  ? "Saving..."
                  : userRating
                    ? "Update Rating"
                    : "Submit Rating"}
              </button>


              {/* Message */}

              {ratingMessage && (
                <p className="mt-4 text-sm text-slate-300">
                  {ratingMessage}
                </p>
              )}

            </>
          ) : (
            <div className="mt-5">

              <p className="text-slate-400">
                Login to rate this movie.
              </p>

              <Link
                to="/login"
                className="mt-4 inline-flex rounded-lg bg-blue-600 px-5 py-3 font-semibold transition hover:bg-blue-500"
              >
                Login to Rate
              </Link>

            </div>
          )}

        </div>

      </section>

    </div>
  );
}

export default MovieDetails;