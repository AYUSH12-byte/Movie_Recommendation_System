import { useEffect, useState } from "react";
import { Link } from "react-router-dom";

import api from "../services/api";
import { useAuth } from "../context/AuthContext";

import MovieGrid from "../components/MovieGrid";
import MovieSearch from "../components/MovieSearch";


function Recommendations() {
  const { user, logout } = useAuth();

  const [personalized, setPersonalized] = useState([]);
  const [popular, setPopular] = useState([]);
  const [trending, setTrending] = useState([]);

  const [loadingPersonalized, setLoadingPersonalized] =
    useState(true);

  const [loadingPopular, setLoadingPopular] =
    useState(true);

  const [loadingTrending, setLoadingTrending] =
    useState(true);

  const [error, setError] = useState("");


  // ============================================================
  // FETCH DATA
  // ============================================================

  useEffect(() => {
    fetchPersonalized();
    fetchPopular();
    fetchTrending();
  }, []);


  // ============================================================
  // PERSONALIZED RECOMMENDATIONS
  // ============================================================

  const fetchPersonalized = async () => {
    try {
      setLoadingPersonalized(true);

      const response = await api.get(
        "/recommendations/personalized?limit=12"
      );

      setPersonalized(
        response.data.recommendations || []
      );

    } catch (error) {
      console.error(
        "Personalized recommendations error:",
        error
      );

      setError(
        error.response?.data?.detail ||
          "Unable to load personalized recommendations."
      );

    } finally {
      setLoadingPersonalized(false);
    }
  };


  // ============================================================
  // POPULAR MOVIES
  // ============================================================

  const fetchPopular = async () => {
    try {
      setLoadingPopular(true);

      const response = await api.get(
        "/movies/popular?limit=12"
      );

      setPopular(
        response.data.movies ||
          response.data ||
          []
      );

    } catch (error) {
      console.error(
        "Popular movies error:",
        error
      );

    } finally {
      setLoadingPopular(false);
    }
  };


  // ============================================================
  // TRENDING MOVIES
  // ============================================================

  const fetchTrending = async () => {
    try {
      setLoadingTrending(true);

      const response = await api.get(
        "/movies/trending?limit=12"
      );

      setTrending(
        response.data.movies ||
          response.data ||
          []
      );

    } catch (error) {
      console.error(
        "Trending movies error:",
        error
      );

    } finally {
      setLoadingTrending(false);
    }
  };


  // ============================================================
  // UI
  // ============================================================

  return (
    <div className="min-h-screen bg-slate-950 text-white">

      {/* ======================================================
          NAVBAR
      ====================================================== */}

      <nav className="sticky top-0 z-50 border-b border-slate-800 bg-slate-950/90 backdrop-blur">

        <div className="mx-auto flex max-w-7xl items-center justify-between px-6 py-4">

          {/* Logo */}
          <Link
            to="/"
            className="text-2xl font-bold tracking-tight"
          >
            Movie
            <span className="text-blue-500">
              AI
            </span>
          </Link>


          {/* Right Side */}
          <div className="flex items-center gap-4">

            <span className="hidden text-sm text-slate-400 sm:block">
              Hi,{" "}
              <span className="font-medium text-white">
                {user?.name || "Movie Lover"}
              </span>{" "}
              👋
            </span>

            <button
              onClick={logout}
              className="rounded-lg border border-slate-700 px-4 py-2 text-sm font-medium text-slate-300 transition hover:border-red-500/50 hover:text-red-400"
            >
              Logout
            </button>

          </div>

        </div>

      </nav>


      {/* ======================================================
          MAIN CONTENT
      ====================================================== */}

      <main className="mx-auto max-w-7xl px-6 py-10">


        {/* ====================================================
            HERO
        ==================================================== */}

        <section className="mb-10">

          <div className="max-w-3xl">

            <p className="mb-3 text-sm font-semibold uppercase tracking-wider text-blue-400">
              AI Movie Recommendation
            </p>

            <h1 className="text-4xl font-bold tracking-tight sm:text-5xl">
              Movies picked
              <span className="text-blue-500">
                {" "}for you.
              </span>
            </h1>

            <p className="mt-4 text-lg leading-8 text-slate-400">
              Discover movies using your ratings,
              movie content, popularity, and
              AI-powered recommendation algorithms.
            </p>

          </div>

        </section>


        {/* ====================================================
            SEARCH
        ==================================================== */}

        <section className="mb-14">
          <MovieSearch />
        </section>


        {/* ====================================================
            ERROR
        ==================================================== */}

        {error && (
          <div className="mb-8 rounded-xl border border-red-500/30 bg-red-500/10 px-5 py-4 text-sm text-red-400">
            {error}
          </div>
        )}


        {/* ====================================================
            PERSONALIZED
        ==================================================== */}

        <section className="mb-16">

          <div className="mb-6">

            <h2 className="text-2xl font-bold">
              Recommended For You
            </h2>

            <p className="mt-1 text-sm text-slate-500">
              AI recommendations based on your
              movie preferences
            </p>

          </div>

          <MovieGrid
            movies={personalized}
            loading={loadingPersonalized}
            emptyMessage="Rate some movies to get personalized recommendations."
          />

        </section>


        {/* ====================================================
            TRENDING
        ==================================================== */}

        <section className="mb-16">

          <div className="mb-6">

            <h2 className="text-2xl font-bold">
              Trending Now 🔥
            </h2>

            <p className="mt-1 text-sm text-slate-500">
              Movies receiving recent attention
              from viewers
            </p>

          </div>

          <MovieGrid
            movies={trending}
            loading={loadingTrending}
            emptyMessage="No trending movies available."
          />

        </section>


        {/* ====================================================
            POPULAR
        ==================================================== */}

        <section className="mb-16">

          <div className="mb-6">

            <h2 className="text-2xl font-bold">
              Popular Movies ⭐
            </h2>

            <p className="mt-1 text-sm text-slate-500">
              Highly rated movies from the community
            </p>

          </div>

          <MovieGrid
            movies={popular}
            loading={loadingPopular}
            emptyMessage="No popular movies available."
          />

        </section>


      </main>


      {/* ======================================================
          FOOTER
      ====================================================== */}

      <footer className="border-t border-slate-800">

        <div className="mx-auto max-w-7xl px-6 py-8 text-center">

          <p className="text-sm text-slate-500">
            MovieAI — AI-powered movie recommendation system
          </p>

          <p className="mt-2 text-xs text-slate-600">
            Content-based filtering • Hybrid recommendation •
            Explainable AI
          </p>

        </div>

      </footer>

    </div>
  );
}

export default Recommendations;