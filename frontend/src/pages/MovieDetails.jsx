import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";

import api from "../services/api";
import MovieCard from "../components/MovieCard";
import Navbar from "../components/Navbar";

function MovieDetails() {
  const { movieId } = useParams();

  const [movie, setMovie] = useState(null);

  const [recommendations, setRecommendations] =
    useState([]);

  const [loading, setLoading] =
    useState(true);

  const [error, setError] =
    useState("");

  useEffect(() => {
    loadMovie();
  }, [movieId]);

  const loadMovie = async () => {
    setLoading(true);
    setError("");

    try {
      const movieResponse =
        await api.get(
          `/movies/${movieId}`
        );

      const movieData =
        movieResponse.data?.movie;

      setMovie(movieData || null);

      if (movieData?.title) {
        try {
          const recommendationResponse =
            await api.get(
              `/recommendations/movie?title=${encodeURIComponent(
                movieData.title
              )}&limit=6`
            );

          setRecommendations(
            recommendationResponse.data
              ?.recommendations || []
          );
        } catch (recommendationError) {
          console.warn(
            "Movie recommendations unavailable:",
            recommendationError
          );

          setRecommendations([]);
        }
      }
    } catch (error) {
      console.error(
        "Failed to load movie:",
        error
      );

      setError(
        error.response?.data?.detail ||
          "Unable to load movie details."
      );
    } finally {
      setLoading(false);
    }
  };

  /* LOADING */

  if (loading) {
    return (
      <LoadingState />
    );
  }

  /* ERROR */

  if (error || !movie) {
    return (
      <div className="min-h-screen bg-slate-950 text-white">
        <Navbar />

        <main className="flex min-h-[70vh] items-center justify-center px-6">
          <div className="text-center">
            <div className="text-6xl">
              🎬
            </div>

            <h1 className="mt-6 text-2xl font-bold">
              Movie Not Found
            </h1>

            <p className="mt-3 text-slate-500">
              {error ||
                "The requested movie could not be found."}
            </p>

            <Link
              to="/"
              className="mt-7 inline-block rounded-xl bg-blue-600 px-6 py-3 font-semibold transition hover:bg-blue-500"
            >
              Back to Home
            </Link>
          </div>
        </main>
      </div>
    );
  }

  const poster =
    movie.posterUrl ||
    movie.poster ||
    null;

  const backdrop =
    movie.backdropUrl ||
    poster ||
    null;

  return (
    <div className="min-h-screen bg-slate-950 text-white">

      {/* NAVBAR */}

      <Navbar />

      {/* MOVIE HERO */}

      <section className="relative min-h-[650px] overflow-hidden">
        {backdrop ? (
          <img
            src={backdrop}
            alt=""
            className="absolute inset-0 h-full w-full object-cover"
          />
        ) : (
          <div className="absolute inset-0 bg-slate-900" />
        )}

        <div className="absolute inset-0 bg-gradient-to-r from-slate-950 via-slate-950/90 to-slate-950/30" />

        <div className="absolute inset-0 bg-gradient-to-t from-slate-950 via-slate-950/40 to-slate-950/20" />

        <div className="relative mx-auto flex min-h-[650px] max-w-7xl items-end px-6 pb-16 pt-32">
          <div className="grid w-full gap-10 md:grid-cols-[250px_1fr]">

            {/* POSTER */}

            <div className="hidden md:block">
              <div className="overflow-hidden rounded-2xl border border-white/10 bg-slate-900 shadow-2xl">
                {poster ? (
                  <img
                    src={poster}
                    alt={movie.title}
                    className="aspect-[2/3] w-full object-cover"
                  />
                ) : (
                  <div className="flex aspect-[2/3] items-center justify-center text-5xl">
                    🎬
                  </div>
                )}
              </div>
            </div>

            {/* MOVIE INFORMATION */}

            <div className="flex flex-col justify-end">

              {/* RATINGS */}

              <div className="mb-4 flex flex-wrap gap-2">
                {movie.tmdbRating !== null &&
                  movie.tmdbRating !== undefined && (
                    <span className="rounded-full bg-yellow-500/15 px-3 py-1 text-sm font-semibold text-yellow-400">
                      ⭐{" "}
                      {Number(
                        movie.tmdbRating
                      ).toFixed(1)}{" "}
                      TMDB
                    </span>
                  )}

                {movie.averageRating !== null &&
                  movie.averageRating !== undefined && (
                    <span className="rounded-full bg-blue-500/15 px-3 py-1 text-sm font-semibold text-blue-400">
                      User Rating{" "}
                      {Number(
                        movie.averageRating
                      ).toFixed(1)}
                    </span>
                  )}

                {movie.releaseDate && (
                  <span className="rounded-full bg-white/10 px-3 py-1 text-sm text-slate-300">
                    {movie.releaseDate.slice(
                      0,
                      4
                    )}
                  </span>
                )}
              </div>

              {/* TITLE */}

              <h1 className="max-w-4xl text-4xl font-black leading-tight md:text-6xl">
                {movie.title}
              </h1>

              {/* GENRES */}

              {movie.genres && (
                <div className="mt-5 flex flex-wrap gap-2">
                  {movie.genres
                    .split("|")
                    .filter(Boolean)
                    .map(
                      (genre) => (
                        <span
                          key={genre}
                          className="rounded-lg border border-slate-700 bg-black/20 px-3 py-1 text-sm text-slate-300 backdrop-blur"
                        >
                          {genre}
                        </span>
                      )
                    )}
                </div>
              )}

              {/* OVERVIEW */}

              {movie.overview && (
                <p className="mt-7 max-w-3xl text-base leading-8 text-slate-300 md:text-lg">
                  {movie.overview}
                </p>
              )}

              {/* ACTIONS */}

              <div className="mt-8 flex flex-wrap gap-4">
                <Link
                  to="/recommendations"
                  className="rounded-xl bg-blue-600 px-6 py-3 font-semibold transition hover:bg-blue-500"
                >
                  Get Similar Movies
                </Link>

                <Link
                  to="/"
                  className="rounded-xl border border-slate-600 bg-black/20 px-6 py-3 font-semibold backdrop-blur transition hover:border-white"
                >
                  Back Home
                </Link>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* MOVIE INFORMATION */}

      <main className="mx-auto max-w-7xl px-6 py-16">
        <section className="grid gap-6 md:grid-cols-3">
          <InfoCard
            title="TMDB Rating"
            value={
              movie.tmdbRating !== null &&
              movie.tmdbRating !== undefined
                ? `⭐ ${Number(
                    movie.tmdbRating
                  ).toFixed(1)}`
                : "Not available"
            }
          />

          <InfoCard
            title="TMDB Votes"
            value={
              movie.tmdbVoteCount !== null &&
              movie.tmdbVoteCount !== undefined
                ? Number(
                    movie.tmdbVoteCount
                  ).toLocaleString()
                : "Not available"
            }
          />

          <InfoCard
            title="Release Date"
            value={
              movie.releaseDate ||
              "Not available"
            }
          />
        </section>

        {/* SIMILAR MOVIES */}

        {recommendations.length > 0 && (
          <section className="mt-20">
            <div className="mb-8">
              <p className="mb-2 text-sm font-semibold uppercase tracking-widest text-blue-500">
                Based on this movie
              </p>

              <h2 className="text-3xl font-bold">
                You May Also Like
              </h2>

              <p className="mt-2 text-slate-500">
                Movies selected using content similarity.
              </p>
            </div>

            <div className="grid grid-cols-2 gap-5 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6">
              {recommendations.map(
                (recommendation) => (
                  <MovieCard
                    key={
                      recommendation.movieId
                    }
                    movie={recommendation}
                  />
                )
              )}
            </div>
          </section>
        )}
      </main>

      {/* FOOTER */}

      <footer className="border-t border-slate-800">
        <div className="mx-auto max-w-7xl px-6 py-8 text-center text-sm text-slate-500">
          MovieAI — AI-powered movie recommendations
        </div>
      </footer>
    </div>
  );
}

/* INFO CARD */

function InfoCard({
  title,
  value
}) {
  return (
    <div className="rounded-2xl border border-slate-800 bg-slate-900/60 p-6">
      <p className="text-sm text-slate-500">
        {title}
      </p>

      <p className="mt-3 text-xl font-bold text-white">
        {value}
      </p>
    </div>
  );
}

/* LOADING STATE */

function LoadingState() {
  return (
    <div className="min-h-screen bg-slate-950">
      <Navbar />

      <div className="mx-auto max-w-7xl px-6 pt-32">
        <div className="grid gap-10 md:grid-cols-[250px_1fr]">
          <div className="hidden aspect-[2/3] animate-pulse rounded-2xl bg-slate-900 md:block" />

          <div className="space-y-6">
            <div className="h-8 w-32 animate-pulse rounded bg-slate-900" />

            <div className="h-16 max-w-2xl animate-pulse rounded bg-slate-900" />

            <div className="h-24 max-w-3xl animate-pulse rounded bg-slate-900" />

            <div className="h-12 w-48 animate-pulse rounded bg-slate-900" />
          </div>
        </div>
      </div>
    </div>
  );
}

export default MovieDetails;