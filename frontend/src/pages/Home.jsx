import { useEffect, useState } from "react";
import { Link } from "react-router-dom";

import api from "../services/api";
import MovieCard from "../components/MovieCard";
import Navbar from "../components/Navbar";

function Home() {
  const [trendingMovies, setTrendingMovies] =
    useState([]);

  const [popularMovies, setPopularMovies] =
    useState([]);

  const [loadingTrending, setLoadingTrending] =
    useState(true);

  const [loadingPopular, setLoadingPopular] =
    useState(true);

  const [error, setError] = useState("");

  useEffect(() => {
    loadMovies();
  }, []);

  const loadMovies = async () => {
    setError("");

    try {
      const [
        trendingResponse,
        popularResponse,
      ] = await Promise.all([
        api.get(
          "/movies/trending?limit=10&days=30"
        ),
        api.get(
          "/movies/popular?limit=10&minimum_ratings=3"
        ),
      ]);

      setTrendingMovies(
        trendingResponse.data?.movies || []
      );

      setPopularMovies(
        popularResponse.data?.movies || []
      );
    } catch (error) {
      console.error(
        "Failed to load home movies:",
        error
      );

      setError(
        "Unable to load movies. Please make sure the backend is running."
      );
    } finally {
      setLoadingTrending(false);
      setLoadingPopular(false);
    }
  };

  const heroMovie =
    trendingMovies.find(
      (movie) => movie.backdropUrl
    ) ||
    trendingMovies[0] ||
    popularMovies[0];

  return (
    <div className="min-h-screen bg-slate-950 text-white">

      {/* NAVBAR */}

      <Navbar />

      {/* HERO */}

      <section className="relative min-h-[650px] overflow-hidden">
        {heroMovie?.backdropUrl ? (
          <img
            src={heroMovie.backdropUrl}
            alt={heroMovie.title}
            className="absolute inset-0 h-full w-full object-cover"
          />
        ) : (
          <div className="absolute inset-0 bg-gradient-to-br from-blue-950 via-slate-950 to-slate-950" />
        )}

        <div className="absolute inset-0 bg-gradient-to-r from-slate-950 via-slate-950/80 to-transparent" />

        <div className="absolute inset-0 bg-gradient-to-t from-slate-950 via-transparent to-slate-950/30" />

        <div className="relative mx-auto flex min-h-[650px] max-w-7xl items-center px-6 pt-20">
          <div className="max-w-2xl">

            <span className="mb-5 inline-flex rounded-full border border-blue-400/20 bg-blue-500/10 px-4 py-2 text-sm font-semibold text-blue-400">
              AI-Powered Movie Recommendations
            </span>

            <h1 className="text-5xl font-black leading-tight tracking-tight md:text-7xl">
              Discover Your Next

              <span className="block text-blue-500">
                Favorite Movie
              </span>
            </h1>

            <p className="mt-6 max-w-xl text-lg leading-8 text-slate-300">
              Discover movies based on your interests,
              ratings, movie similarity, popularity,
              and intelligent recommendation algorithms.
            </p>

            <div className="mt-8 flex flex-wrap gap-4">
              <Link
                to="/recommendations"
                className="rounded-xl bg-blue-600 px-6 py-3 font-semibold text-white transition hover:bg-blue-500"
              >
                Get Recommendations
              </Link>

              {heroMovie?.movieId && (
                <Link
                  to={`/movie/${heroMovie.movieId}`}
                  className="rounded-xl border border-slate-600 bg-black/20 px-6 py-3 font-semibold text-white backdrop-blur transition hover:border-white"
                >
                  View Movie
                </Link>
              )}
            </div>
          </div>
        </div>
      </section>

      {/* MAIN CONTENT */}

      <main className="mx-auto max-w-7xl px-6 py-16">

        {/* ERROR */}

        {error && (
          <div className="mb-10 rounded-xl border border-red-500/20 bg-red-500/10 px-5 py-4 text-sm text-red-300">
            {error}
          </div>
        )}

        {/* TRENDING MOVIES */}

        <section className="mb-16">
          <div className="mb-7 flex items-end justify-between">
            <div>
              <p className="mb-2 text-sm font-semibold uppercase tracking-widest text-blue-500">
                What's hot
              </p>

              <h2 className="text-3xl font-bold">
                Trending Movies
              </h2>
            </div>

            <span className="hidden text-sm text-slate-500 sm:block">
              Last 30 days
            </span>
          </div>

          {loadingTrending ? (
            <MovieSkeleton />
          ) : trendingMovies.length > 0 ? (
            <div className="grid grid-cols-2 gap-5 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5">
              {trendingMovies.map(
                (movie) => (
                  <MovieCard
                    key={movie.movieId}
                    movie={movie}
                  />
                )
              )}
            </div>
          ) : (
            <EmptyState
              message="No trending movies available yet."
            />
          )}
        </section>

        {/* POPULAR MOVIES */}

        <section className="mb-16">
          <div className="mb-7">
            <p className="mb-2 text-sm font-semibold uppercase tracking-widest text-blue-500">
              Most watched
            </p>

            <h2 className="text-3xl font-bold">
              Popular Movies
            </h2>
          </div>

          {loadingPopular ? (
            <MovieSkeleton />
          ) : popularMovies.length > 0 ? (
            <div className="grid grid-cols-2 gap-5 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5">
              {popularMovies.map(
                (movie) => (
                  <MovieCard
                    key={movie.movieId}
                    movie={movie}
                  />
                )
              )}
            </div>
          ) : (
            <EmptyState
              message="No popular movies available yet."
            />
          )}
        </section>

        {/* PERSONALIZED CTA */}

        <section className="overflow-hidden rounded-3xl border border-blue-500/20 bg-gradient-to-br from-blue-600/20 via-slate-900 to-slate-900 p-8 md:p-12">
          <div className="max-w-2xl">
            <p className="text-sm font-semibold uppercase tracking-widest text-blue-400">
              Personalized for you
            </p>

            <h2 className="mt-3 text-3xl font-bold md:text-4xl">
              Let AI find movies you'll love.
            </h2>

            <p className="mt-4 leading-7 text-slate-400">
              Rate movies you have watched and our
              recommendation engine will learn your
              preferences and suggest movies based on
              your taste.
            </p>

            <Link
              to="/recommendations"
              className="mt-7 inline-block rounded-xl bg-blue-600 px-6 py-3 font-semibold text-white transition hover:bg-blue-500"
            >
              Explore Recommendations
            </Link>
          </div>
        </section>
      </main>

      {/* FOOTER */}

      <footer className="border-t border-slate-800">
        <div className="mx-auto flex max-w-7xl flex-col gap-4 px-6 py-8 text-sm text-slate-500 sm:flex-row sm:items-center sm:justify-between">
          <p>
            © {new Date().getFullYear()} MovieAI
          </p>

          <p>
            AI-powered movie recommendation system
          </p>
        </div>
      </footer>
    </div>
  );
}

/* LOADING SKELETON */

function MovieSkeleton() {
  return (
    <div className="grid grid-cols-2 gap-5 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5">
      {Array.from({ length: 5 }).map(
        (_, index) => (
          <div
            key={index}
            className="overflow-hidden rounded-xl border border-slate-800 bg-slate-900"
          >
            <div className="aspect-[2/3] animate-pulse bg-slate-800" />

            <div className="space-y-3 p-4">
              <div className="h-4 animate-pulse rounded bg-slate-800" />

              <div className="h-3 w-2/3 animate-pulse rounded bg-slate-800" />
            </div>
          </div>
        )
      )}
    </div>
  );
}

/* EMPTY STATE */

function EmptyState({ message }) {
  return (
    <div className="rounded-xl border border-slate-800 bg-slate-900/50 px-6 py-12 text-center">
      <div className="text-4xl">
        🎬
      </div>

      <p className="mt-4 text-sm text-slate-500">
        {message}
      </p>
    </div>
  );
}

export default Home;