import { useEffect, useState } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";

import api from "../services/api";
import { useAuth } from "../context/AuthContext";

function MovieDetails() {
  const { movieId } = useParams();
  const navigate = useNavigate();

  const { user, isAuthenticated } = useAuth();

  const [movie, setMovie] = useState(null);
  const [rating, setRating] = useState(null);
  const [selectedRating, setSelectedRating] = useState(0);

  const [loading, setLoading] = useState(true);
  const [ratingLoading, setRatingLoading] = useState(false);

  const [error, setError] = useState("");
  const [message, setMessage] = useState("");


  // FETCH MOVIE

  useEffect(() => {
    fetchMovie();
  }, [movieId]);

  const fetchMovie = async () => {
    try {
      setLoading(true);
      setError("");

      const response = await api.get(
        `/movies/${movieId}`
      );

      console.log(
        "MOVIE DETAILS:",
        response.data
      );

      setMovie(
        response.data.movie ||
        response.data
      );
    } catch (error) {
      console.error(
        "Failed to load movie:",
        error
      );

      setError(
        error.response?.data?.detail ||
        "Movie could not be loaded."
      );
    } finally {
      setLoading(false);
    }
  };


  // FETCH USER RATING

  useEffect(() => {
    if (
      isAuthenticated &&
      movieId
    ) {
      fetchUserRating();
    }
  }, [isAuthenticated, movieId]);

  const fetchUserRating = async () => {
    try {
      const response = await api.get(
        `/ratings/movie/${movieId}`
      );

      const data = response.data;

      const userRating =
        data.rating ??
        data.userRating ??
        data;

      if (
        userRating &&
        typeof userRating === "object"
      ) {
        setRating(userRating);

        setSelectedRating(
          Number(
            userRating.rating || 0
          )
        );
      }
    } catch (error) {
      if (
        error.response?.status !== 404
      ) {
        console.error(
          "Failed to load rating:",
          error
        );
      }

      setRating(null);
    }
  };


  // SUBMIT RATING

  const submitRating = async () => {
    if (!isAuthenticated) {
      navigate("/login");
      return;
    }

    if (
      selectedRating < 0.5 ||
      selectedRating > 5
    ) {
      setError(
        "Please select a rating between 0.5 and 5."
      );

      return;
    }

    try {
      setRatingLoading(true);
      setError("");
      setMessage("");

      await api.post(
        "/ratings/",
        {
          movieId: Number(movieId),
          rating: selectedRating,
        }
      );

      setMessage(
        "Your rating has been saved successfully."
      );

      await fetchUserRating();
      await fetchMovie();
    } catch (error) {
      console.error(
        "Failed to save rating:",
        error
      );

      setError(
        error.response?.data?.detail ||
        "Failed to save your rating."
      );
    } finally {
      setRatingLoading(false);
    }
  };


  // LOADING

  if (loading) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-slate-950 text-white">
        <div className="text-center">

          <div className="mb-3 text-5xl animate-pulse">
            🎬
          </div>

          <p className="text-slate-400">
            Loading movie...
          </p>

        </div>
      </div>
    );
  }


  // ERROR

  if (error && !movie) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-slate-950 px-6 text-white">
        <div className="max-w-md text-center">

          <div className="mb-4 text-5xl">
            😕
          </div>

          <h1 className="text-2xl font-bold">
            Movie not found
          </h1>

          <p className="mt-2 text-slate-400">
            {error}
          </p>

          <Link
            to="/recommendations"
            className="mt-6 inline-block rounded-lg bg-blue-600 px-5 py-3 font-semibold transition hover:bg-blue-700"
          >
            Back to Movies
          </Link>

        </div>
      </div>
    );
  }


  // MOVIE DATA

  const posterUrl =
    movie?.posterUrl ||
    movie?.poster ||
    null;

  const backdropUrl =
    movie?.backdropUrl ||
    null;

  const overview =
    movie?.overview ||
    "No overview available for this movie.";

  const releaseDate =
    movie?.releaseDate ||
    "";

  const averageRating =
    movie?.averageRating ??
    null;

  const tmdbRating =
    movie?.tmdbRating ??
    null;

  const tmdbVoteCount =
    movie?.tmdbVoteCount ??
    null;

  const totalRatings =
    movie?.totalRatings ??
    null;

  const genres = movie?.genres
    ? movie.genres
        .split("|")
        .filter(Boolean)
    : [];


  return (
    <div className="min-h-screen bg-slate-950 text-white">

      {/* NAVBAR */}

      <nav className="border-b border-slate-800 bg-slate-950/95 backdrop-blur">
        <div className="mx-auto flex max-w-7xl items-center justify-between px-6 py-4">

          <Link
            to="/"
            className="text-2xl font-bold"
          >
            Movie
            <span className="text-blue-500">
              AI
            </span>
          </Link>

          <div className="flex items-center gap-5">

            <Link
              to="/recommendations"
              className="text-sm text-slate-400 transition hover:text-white"
            >
              Movies
            </Link>

            {isAuthenticated ? (
              <span className="hidden text-sm text-slate-400 sm:block">
                {user?.name}
              </span>
            ) : (
              <Link
                to="/login"
                className="rounded-lg bg-blue-600 px-4 py-2 text-sm font-semibold transition hover:bg-blue-700"
              >
                Login
              </Link>
            )}

          </div>
        </div>
      </nav>


      {/* HERO */}

      <section className="relative overflow-hidden">

        {/* Backdrop */}

        {backdropUrl && (
          <div
            className="absolute inset-0 bg-cover bg-center opacity-30"
            style={{
              backgroundImage: `url("${backdropUrl}")`,
            }}
          />
        )}

        {/* Overlay */}

        <div className="absolute inset-0 bg-gradient-to-r from-slate-950 via-slate-950/95 to-slate-950/70" />

        <div className="absolute inset-0 bg-gradient-to-t from-slate-950 via-transparent to-slate-950/40" />


        {/* Content */}

        <div className="relative mx-auto max-w-7xl px-6 py-10 md:py-16">

          {/* Back */}

          <Link
            to="/recommendations"
            className="mb-8 inline-flex items-center gap-2 text-sm text-slate-400 transition hover:text-white"
          >
            ← Back to movies
          </Link>

          <div className="grid gap-10 md:grid-cols-[280px_1fr] lg:grid-cols-[320px_1fr]">


            {/* POSTER */}

            <div>
              <div className="overflow-hidden rounded-2xl border border-slate-700 bg-slate-900 shadow-2xl">

                {posterUrl ? (
                  <img
                    src={posterUrl}
                    alt={movie.title}
                    className="h-auto w-full object-cover"
                    onError={(event) => {
                      event.currentTarget.style.display =
                        "none";
                    }}
                  />
                ) : (
                  <div className="flex aspect-[2/3] flex-col items-center justify-center gap-3">

                    <span className="text-6xl">
                      🎬
                    </span>

                    <span className="text-sm text-slate-500">
                      No poster available
                    </span>

                  </div>
                )}

              </div>
            </div>


            {/* INFORMATION */}

            <div className="flex flex-col justify-center">

              <p className="mb-3 text-sm font-semibold uppercase tracking-widest text-blue-400">
                Movie Details
              </p>

              <h1 className="text-4xl font-black leading-tight sm:text-5xl lg:text-6xl">
                {movie.title}
              </h1>


              {/* META */}

              <div className="mt-6 flex flex-wrap items-center gap-3">

                {releaseDate && (
                  <span className="rounded-lg border border-slate-700 bg-slate-900/80 px-3 py-2 text-sm text-slate-300">
                    📅 {releaseDate}
                  </span>
                )}

                {averageRating !== null && (
                  <span className="rounded-lg border border-yellow-500/20 bg-yellow-500/10 px-3 py-2 text-sm font-semibold text-yellow-400">
                    ⭐{" "}
                    {Number(
                      averageRating
                    ).toFixed(1)}
                    /5
                  </span>
                )}

                {totalRatings !== null && (
                  <span className="rounded-lg border border-slate-700 bg-slate-900/80 px-3 py-2 text-sm text-slate-300">
                    👥{" "}
                    {Number(
                      totalRatings
                    ).toLocaleString()}{" "}
                    ratings
                  </span>
                )}

              </div>


              {/* GENRES */}

              {genres.length > 0 && (
                <div className="mt-6 flex flex-wrap gap-2">

                  {genres.map((genre) => (
                    <span
                      key={genre}
                      className="rounded-full border border-slate-700 bg-slate-900/80 px-3 py-1.5 text-xs font-medium text-slate-300"
                    >
                      {genre}
                    </span>
                  ))}

                </div>
              )}


              {/* OVERVIEW */}

              <div className="mt-8 max-w-3xl">

                <h2 className="mb-3 text-xl font-bold">
                  Overview
                </h2>

                <p className="text-base leading-8 text-slate-300">
                  {overview}
                </p>

              </div>


              {/* TMDB INFORMATION */}

              {(tmdbRating !== null ||
                tmdbVoteCount !== null) && (
                <div className="mt-6 flex flex-wrap gap-4">

                  {tmdbRating !== null && (
                    <div className="rounded-xl border border-slate-800 bg-slate-900/70 px-5 py-4">

                      <p className="text-xs uppercase tracking-wide text-slate-500">
                        TMDB Rating
                      </p>

                      <p className="mt-1 text-xl font-bold text-yellow-400">
                        ⭐{" "}
                        {Number(
                          tmdbRating
                        ).toFixed(1)}
                        /10
                      </p>

                    </div>
                  )}

                  {tmdbVoteCount !== null && (
                    <div className="rounded-xl border border-slate-800 bg-slate-900/70 px-5 py-4">

                      <p className="text-xs uppercase tracking-wide text-slate-500">
                        TMDB Votes
                      </p>

                      <p className="mt-1 text-xl font-bold">
                        {Number(
                          tmdbVoteCount
                        ).toLocaleString()}
                      </p>

                    </div>
                  )}

                </div>
              )}


              {/* USER RATING */}

              <div className="mt-10 max-w-xl rounded-2xl border border-slate-800 bg-slate-900/90 p-6 shadow-xl">

                <h2 className="text-xl font-bold">
                  Rate this movie
                </h2>

                <p className="mt-1 text-sm text-slate-500">
                  Your rating helps improve your AI recommendations.
                </p>


                {/* Stars */}

                <div className="mt-5 flex gap-2">

                  {[1, 2, 3, 4, 5].map(
                    (value) => (
                      <button
                        key={value}
                        type="button"
                        onClick={() =>
                          setSelectedRating(
                            value
                          )
                        }
                        className={`text-3xl transition hover:scale-110 ${
                          selectedRating >=
                          value
                            ? "text-yellow-400"
                            : "text-slate-700 hover:text-yellow-400"
                        }`}
                      >
                        ★
                      </button>
                    )
                  )}

                </div>

                {selectedRating > 0 && (
                  <p className="mt-2 text-sm text-slate-400">
                    You selected{" "}
                    <span className="font-semibold text-white">
                      {selectedRating}/5
                    </span>
                  </p>
                )}


                {/* Existing rating */}

                {rating && (
                  <p className="mt-2 text-sm text-green-400">
                    Your current rating:{" "}
                    {rating.rating}/5
                  </p>
                )}


                {/* Button */}

                {!isAuthenticated ? (
                  <Link
                    to="/login"
                    className="mt-5 inline-block rounded-lg bg-blue-600 px-5 py-3 font-semibold transition hover:bg-blue-700"
                  >
                    Login to Rate
                  </Link>
                ) : (
                  <button
                    type="button"
                    onClick={submitRating}
                    disabled={ratingLoading}
                    className="mt-5 rounded-lg bg-blue-600 px-5 py-3 font-semibold transition hover:bg-blue-700 disabled:cursor-not-allowed disabled:opacity-60"
                  >
                    {ratingLoading
                      ? "Saving..."
                      : rating
                        ? "Update Rating"
                        : "Submit Rating"}
                  </button>
                )}


                {/* Success */}

                {message && (
                  <p className="mt-4 text-sm text-green-400">
                    {message}
                  </p>
                )}


                {/* Error */}

                {error && (
                  <p className="mt-4 text-sm text-red-400">
                    {error}
                  </p>
                )}

              </div>

            </div>
          </div>
        </div>
      </section>


      {/* FOOTER */}

      <footer className="border-t border-slate-800 bg-slate-950">
        <div className="mx-auto max-w-7xl px-6 py-8 text-center text-sm text-slate-500">
          Movie Recommendation System
        </div>
      </footer>

    </div>
  );
}

export default MovieDetails;