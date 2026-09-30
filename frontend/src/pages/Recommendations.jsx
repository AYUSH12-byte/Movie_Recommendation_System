import { useEffect, useState } from "react";
import { Link } from "react-router-dom";

import api from "../services/api";
import MovieCard from "../components/MovieCard";
import Navbar from "../components/Navbar";

function Recommendations() {
  const [recommendations, setRecommendations] =
    useState([]);

  const [loading, setLoading] =
    useState(true);

  const [error, setError] =
    useState("");

  const [hasProfile, setHasProfile] =
    useState(false);

  const [
    recommendationType,
    setRecommendationType,
  ] = useState("");

  const [message, setMessage] =
    useState("");

  const [algorithm, setAlgorithm] =
    useState(null);

  useEffect(() => {
    loadRecommendations();
  }, []);

  const loadRecommendations = async () => {
    setLoading(true);
    setError("");

    try {
      const response = await api.get(
        "/recommendations/personalized?limit=12"
      );

      const data = response.data;

      setRecommendations(
        data?.recommendations || []
      );

      setHasProfile(
        Boolean(data?.hasProfile)
      );

      setRecommendationType(
        data?.recommendationType || ""
      );

      setMessage(
        data?.message || ""
      );

      setAlgorithm(
        data?.algorithm || null
      );
    } catch (error) {
      console.error(
        "Failed to load recommendations:",
        error
      );

      if (
        error.response?.status === 401
      ) {
        setError(
          "Please login to get personalized recommendations."
        );
      } else {
        setError(
          error.response?.data?.detail ||
            "Unable to load recommendations."
        );
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-950 text-white">

      {/* NAVBAR */}

      <Navbar />

      <main className="mx-auto max-w-7xl px-6 pb-20 pt-32">

        {/* HEADER */}

        <section className="mb-12">
          <div className="max-w-3xl">
            <div className="mb-4 inline-flex rounded-full border border-blue-400/20 bg-blue-500/10 px-4 py-2 text-sm font-semibold text-blue-400">
              AI Recommendation Engine
            </div>

            <h1 className="text-4xl font-black tracking-tight md:text-6xl">
              Movies Picked

              <span className="text-blue-500">
                {" "}For You
              </span>
            </h1>

            <p className="mt-5 max-w-2xl text-lg leading-8 text-slate-400">
              Our recommendation engine analyzes your
              movie ratings, content similarity,
              popularity, and preference patterns to
              discover movies you may enjoy.
            </p>
          </div>
        </section>

        {/* ERROR */}

        {error && (
          <section className="mb-10 rounded-2xl border border-yellow-500/20 bg-yellow-500/10 p-6">
            <div className="flex flex-col gap-5 sm:flex-row sm:items-center sm:justify-between">
              <div>
                <h2 className="font-semibold text-yellow-300">
                  Login required
                </h2>

                <p className="mt-1 text-sm text-yellow-200/70">
                  {error}
                </p>
              </div>

              <Link
                to="/login"
                className="rounded-xl bg-blue-600 px-5 py-3 text-center text-sm font-semibold transition hover:bg-blue-500"
              >
                Login
              </Link>
            </div>
          </section>
        )}

        {/* LOADING */}

        {loading && (
          <RecommendationSkeleton />
        )}

        {/* RECOMMENDATIONS */}

        {!loading &&
          recommendations.length > 0 && (
            <>
              {/* INFO CARDS */}

              <section className="mb-10 grid gap-5 md:grid-cols-3">
                <InfoCard
                  title="Recommendation Type"
                  value={
                    recommendationType ===
                    "hybrid"
                      ? "Hybrid AI"
                      : "Cold Start"
                  }
                />

                <InfoCard
                  title="Movies Found"
                  value={
                    recommendations.length
                  }
                />

                <InfoCard
                  title="User Profile"
                  value={
                    hasProfile
                      ? "Personalized"
                      : "Building Profile"
                  }
                />
              </section>

              {/* MESSAGE */}

              {message && (
                <section className="mb-10 rounded-2xl border border-slate-800 bg-slate-900/60 p-6">
                  <div className="flex gap-4">
                    <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-blue-500/10 text-xl">
                      🤖
                    </div>

                    <div>
                      <h2 className="font-semibold">
                        Recommendation Engine
                      </h2>

                      <p className="mt-2 text-sm leading-6 text-slate-400">
                        {message}
                      </p>
                    </div>
                  </div>
                </section>
              )}

              {/* MOVIES */}

              <section>
                <div className="mb-7 flex items-end justify-between">
                  <div>
                    <p className="mb-2 text-sm font-semibold uppercase tracking-widest text-blue-500">
                      AI selected
                    </p>

                    <h2 className="text-3xl font-bold">
                      Recommended Movies
                    </h2>
                  </div>

                  <button
                    type="button"
                    onClick={
                      loadRecommendations
                    }
                    className="rounded-lg border border-slate-700 px-4 py-2 text-sm text-slate-300 transition hover:border-blue-500 hover:text-white"
                  >
                    Refresh
                  </button>
                </div>

                <div className="grid grid-cols-2 gap-5 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6">
                  {recommendations.map(
                    (movie) => (
                      <div
                        key={
                          movie.movieId
                        }
                        className="group"
                      >
                        <MovieCard
                          movie={movie}
                        />

                        <RecommendationReason
                          movie={movie}
                        />
                      </div>
                    )
                  )}
                </div>
              </section>

              {/* ALGORITHM */}

              {algorithm && (
                <AlgorithmSection
                  algorithm={algorithm}
                />
              )}
            </>
          )}

        {/* EMPTY */}

        {!loading &&
          !error &&
          recommendations.length === 0 && (
            <EmptyRecommendations
              onRefresh={
                loadRecommendations
              }
            />
          )}
      </main>

      <Footer />
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

      <p className="mt-3 text-xl font-bold">
        {value}
      </p>
    </div>
  );
}

/* RECOMMENDATION REASON */

function RecommendationReason({
  movie
}) {
  if (!movie.reason) {
    return null;
  }

  return (
    <div className="mt-3 rounded-lg border border-slate-800 bg-slate-900/60 p-3">
      <p className="text-[11px] font-semibold uppercase tracking-wider text-blue-400">
        Why this movie?
      </p>

      <p className="mt-1 line-clamp-3 text-xs leading-5 text-slate-500">
        {movie.reason}
      </p>
    </div>
  );
}

/* ALGORITHM SECTION */

function AlgorithmSection({
  algorithm
}) {
  const entries =
    Object.entries(algorithm);

  if (!entries.length) {
    return null;
  }

  return (
    <section className="mt-20 rounded-3xl border border-slate-800 bg-slate-900/40 p-7 md:p-10">
      <div className="mb-8">
        <p className="text-sm font-semibold uppercase tracking-widest text-blue-500">
          Recommendation engine
        </p>

        <h2 className="mt-2 text-2xl font-bold">
          How recommendations are generated
        </h2>

        <p className="mt-3 max-w-2xl text-sm leading-6 text-slate-500">
          The system combines multiple signals rather
          than relying on a single similarity score.
        </p>
      </div>

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {entries.map(
          ([key, value]) => (
            <div
              key={key}
              className="rounded-xl border border-slate-800 bg-slate-950/70 p-5"
            >
              <p className="text-xs uppercase tracking-wider text-slate-500">
                {formatLabel(key)}
              </p>

              <p className="mt-3 text-2xl font-bold text-blue-400">
                {typeof value ===
                "number"
                  ? value <= 1
                    ? `${(
                        value * 100
                      ).toFixed(0)}%`
                    : value
                  : String(value)}
              </p>
            </div>
          )
        )}
      </div>
    </section>
  );
}

/* FORMAT LABEL */

function formatLabel(value) {
  return value
    .replace(
      /([A-Z])/g,
      " $1"
    )
    .replace(
      /_/g,
      " "
    )
    .replace(
      /^./,
      (char) =>
        char.toUpperCase()
    );
}

/* LOADING SKELETON */

function RecommendationSkeleton() {
  return (
    <div>
      <div className="mb-10 grid gap-5 md:grid-cols-3">
        {Array.from({
          length: 3,
        }).map(
          (_, index) => (
            <div
              key={index}
              className="h-28 animate-pulse rounded-2xl bg-slate-900"
            />
          )
        )}
      </div>

      <div className="grid grid-cols-2 gap-5 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6">
        {Array.from({
          length: 12,
        }).map(
          (_, index) => (
            <div
              key={index}
              className="overflow-hidden rounded-xl bg-slate-900"
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
    </div>
  );
}

/* EMPTY RECOMMENDATIONS */

function EmptyRecommendations({
  onRefresh
}) {
  return (
    <section className="flex min-h-[400px] items-center justify-center rounded-3xl border border-slate-800 bg-slate-900/30">
      <div className="max-w-lg px-6 text-center">
        <div className="text-6xl">
          🤖
        </div>

        <h2 className="mt-6 text-2xl font-bold">
          We need a little more information
        </h2>

        <p className="mt-3 leading-7 text-slate-500">
          Rate a few movies and the recommendation
          engine can start learning your preferences.
        </p>

        <div className="mt-7 flex justify-center gap-3">
          <Link
            to="/"
            className="rounded-xl bg-blue-600 px-5 py-3 font-semibold transition hover:bg-blue-500"
          >
            Explore Movies
          </Link>

          <button
            type="button"
            onClick={onRefresh}
            className="rounded-xl border border-slate-700 px-5 py-3 font-semibold transition hover:border-blue-500"
          >
            Refresh
          </button>
        </div>
      </div>
    </section>
  );
}

/* FOOTER */

function Footer() {
  return (
    <footer className="border-t border-slate-800">
      <div className="mx-auto max-w-7xl px-6 py-8 text-center text-sm text-slate-500">
        MovieAI — AI-powered movie recommendation system
      </div>
    </footer>
  );
}

export default Recommendations;