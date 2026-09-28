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

  // ============================================================
  // FETCH MOVIE
  // ============================================================

  useEffect(() => {
    fetchMovie();
  }, [movieId]);

  const fetchMovie = async () => {
    try {
      setLoading(true);
      setError("");

      const response = await api.get(`/movies/${movieId}`);

      setMovie(response.data.movie || response.data);
    } catch (error) {
      console.error(error);

      setError(error.response?.data?.detail || "Movie could not be loaded.");
    } finally {
      setLoading(false);
    }
  };

  // ============================================================
  // FETCH USER RATING
  // ============================================================

  useEffect(() => {
    if (isAuthenticated && movieId) {
      fetchUserRating();
    }
  }, [isAuthenticated, movieId]);

  const fetchUserRating = async () => {
    try {
      const response = await api.get(`/ratings/movie/${movieId}`);

      const data = response.data;

      const userRating = data.rating ?? data.userRating ?? data;

      if (userRating && typeof userRating === "object") {
        setRating(userRating);
        setSelectedRating(Number(userRating.rating || 0));
      }
    } catch (error) {
      // 404 means user has not rated this movie.
      if (error.response?.status !== 404) {
        console.error("Failed to load rating:", error);
      }
    }
  };

  // ============================================================
  // SUBMIT RATING
  // ============================================================

  const submitRating = async () => {
    if (!isAuthenticated) {
      navigate("/login");
      return;
    }

    if (selectedRating < 0.5 || selectedRating > 5) {
      setError("Please select a rating between 0.5 and 5.");

      return;
    }

    try {
      setRatingLoading(true);
      setError("");
      setMessage("");

      await api.post("/ratings/", {
        movieId: Number(movieId),
        rating: selectedRating,
      });

      setMessage("Your rating has been saved successfully.");

      await fetchUserRating();
      await fetchMovie();
    } catch (error) {
      console.error(error);

      setError(error.response?.data?.detail || "Failed to save your rating.");
    } finally {
      setRatingLoading(false);
    }
  };

  // ============================================================
  // LOADING
  // ============================================================

  if (loading) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-slate-950 text-white">
        <div className="text-center">
          <div className="mb-3 text-4xl">🎬</div>

          <p className="text-slate-400">Loading movie...</p>
        </div>
      </div>
    );
  }

  // ============================================================
  // ERROR
  // ============================================================

  if (error && !movie) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-slate-950 px-6 text-white">
        <div className="text-center">
          <div className="mb-4 text-5xl">😕</div>

          <h1 className="text-2xl font-bold">Movie not found</h1>

          <p className="mt-2 text-slate-400">{error}</p>

          <Link
            to="/recommendations"
            className="mt-6 inline-block rounded-lg bg-blue-600 px-5 py-3 font-semibold hover:bg-blue-700"
          >
            Back to Movies
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-950 text-white">
      {/* Navbar */}
      <nav className="border-b border-slate-800 bg-slate-950">
        <div className="mx-auto flex max-w-7xl items-center justify-between px-6 py-4">
          <Link to="/" className="text-2xl font-bold">
            Movie<span className="text-blue-500">AI</span>
          </Link>

          <div className="flex items-center gap-4">
            <Link
              to="/recommendations"
              className="text-sm text-slate-400 hover:text-white"
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
                className="rounded-lg bg-blue-600 px-4 py-2 text-sm font-semibold hover:bg-blue-700"
              >
                Login
              </Link>
            )}
          </div>
        </div>
      </nav>

      {/* Movie */}
      <main className="mx-auto max-w-7xl px-6 py-10">
        <Link
          to="/recommendations"
          className="mb-8 inline-block text-sm text-slate-400 hover:text-white"
        >
          ← Back to movies
        </Link>

        <div className="grid gap-10 md:grid-cols-[280px_1fr]">
          {/* Poster */}
          <div>
            <div className="overflow-hidden rounded-2xl border border-slate-800 bg-slate-900 shadow-xl">
              {movie.posterUrl ? (
                <img
                  src={movie.posterUrl}
                  alt={movie.title}
                  className="w-full object-cover"
                />
              ) : (
                <div className="flex aspect-[2/3] items-center justify-center text-6xl">
                  🎬
                </div>
              )}
            </div>
          </div>

          {/* Information */}
          <div>
            <p className="mb-3 text-sm font-semibold uppercase tracking-wider text-blue-400">
              Movie Details
            </p>

            <h1 className="text-4xl font-bold sm:text-5xl">{movie.title}</h1>

            {/* Genres */}
            {movie.genres && (
              <div className="mt-5 flex flex-wrap gap-2">
                {movie.genres.split("|").map((genre) => (
                  <span
                    key={genre}
                    className="rounded-full border border-slate-700 bg-slate-900 px-3 py-1 text-sm text-slate-300"
                  >
                    {genre}
                  </span>
                ))}
              </div>
            )}

            {/* Rating */}
            <div className="mt-6 flex flex-wrap gap-5">
              {movie.averageRating !== undefined && (
                <div>
                  <p className="text-sm text-slate-500">Community Rating</p>

                  <p className="mt-1 text-2xl font-bold">
                    ⭐ {Number(movie.averageRating).toFixed(1)}
                  </p>
                </div>
              )}

              {movie.totalRatings !== undefined && (
                <div>
                  <p className="text-sm text-slate-500">Ratings</p>

                  <p className="mt-1 text-2xl font-bold">
                    {movie.totalRatings}
                  </p>
                </div>
              )}
            </div>

            {/* User Rating */}
            <div className="mt-10 max-w-xl rounded-2xl border border-slate-800 bg-slate-900 p-6">
              <h2 className="text-xl font-bold">Rate this movie</h2>

              <p className="mt-1 text-sm text-slate-500">
                Your rating helps improve your AI recommendations.
              </p>

              {/* Stars */}
              <div className="mt-5 flex flex-wrap gap-2">
                {[1, 2, 3, 4, 5].map((value) => (
                  <button
                    key={value}
                    type="button"
                    onClick={() => setSelectedRating(value)}
                    className={`text-3xl transition ${
                      selectedRating >= value
                        ? "text-yellow-400"
                        : "text-slate-700 hover:text-yellow-400"
                    }`}
                  >
                    ★
                  </button>
                ))}
              </div>

              {selectedRating > 0 && (
                <p className="mt-2 text-sm text-slate-400">
                  You selected{" "}
                  <span className="font-semibold text-white">
                    {selectedRating}/5
                  </span>
                </p>
              )}

              {rating && (
                <p className="mt-2 text-sm text-green-400">
                  Your current rating: {rating.rating}/5
                </p>
              )}

              {!isAuthenticated ? (
                <Link
                  to="/login"
                  className="mt-5 inline-block rounded-lg bg-blue-600 px-5 py-3 font-semibold hover:bg-blue-700"
                >
                  Login to Rate
                </Link>
              ) : (
                <button
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

              {message && (
                <p className="mt-4 text-sm text-green-400">{message}</p>
              )}

              {error && <p className="mt-4 text-sm text-red-400">{error}</p>}
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}

export default MovieDetails;
