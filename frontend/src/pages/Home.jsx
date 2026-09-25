import { Link } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

function Home() {
  const {
    user,
    isAuthenticated,
    logout,
  } = useAuth();

  return (
    <div className="min-h-screen bg-slate-950 text-white">

      {/* Navbar */}
      <nav className="border-b border-slate-800 bg-slate-950/95">
        <div className="mx-auto flex max-w-7xl items-center justify-between px-6 py-4">

          <Link
            to="/"
            className="text-xl font-bold tracking-tight"
          >
            Movie<span className="text-blue-500">AI</span>
          </Link>

          <div className="flex items-center gap-3">

            {isAuthenticated ? (
              <>
                <Link
                  to="/recommendations"
                  className="rounded-lg bg-blue-600 px-4 py-2 text-sm font-medium transition hover:bg-blue-700"
                >
                  My Recommendations
                </Link>

                <button
                  onClick={logout}
                  className="rounded-lg border border-slate-700 px-4 py-2 text-sm font-medium transition hover:bg-slate-800"
                >
                  Logout
                </button>
              </>
            ) : (
              <>
                <Link
                  to="/login"
                  className="rounded-lg px-4 py-2 text-sm font-medium text-slate-300 transition hover:text-white"
                >
                  Login
                </Link>

                <Link
                  to="/register"
                  className="rounded-lg bg-blue-600 px-4 py-2 text-sm font-medium transition hover:bg-blue-700"
                >
                  Register
                </Link>
              </>
            )}

          </div>
        </div>
      </nav>

      {/* Hero */}
      <main>

        <section className="mx-auto max-w-7xl px-6 py-24">

          <div className="max-w-3xl">

            <div className="mb-6 inline-flex rounded-full border border-blue-500/30 bg-blue-500/10 px-4 py-2 text-sm text-blue-400">
              AI-Powered Movie Recommendation
            </div>

            <h1 className="text-5xl font-bold leading-tight tracking-tight md:text-6xl">

              Discover Movies
              <span className="block text-blue-500">
                You'll Love.
              </span>

            </h1>

            <p className="mt-6 max-w-2xl text-lg leading-8 text-slate-400">

              Get personalized movie recommendations
              using content-based filtering, user
              preferences, popularity, and hybrid
              recommendation techniques.

            </p>

            <div className="mt-8 flex flex-wrap gap-4">

              {isAuthenticated ? (
                <Link
                  to="/recommendations"
                  className="rounded-xl bg-blue-600 px-6 py-3 font-semibold transition hover:bg-blue-700"
                >
                  Explore Recommendations
                </Link>
              ) : (
                <>
                  <Link
                    to="/register"
                    className="rounded-xl bg-blue-600 px-6 py-3 font-semibold transition hover:bg-blue-700"
                  >
                    Get Started
                  </Link>

                  <Link
                    to="/login"
                    className="rounded-xl border border-slate-700 px-6 py-3 font-semibold text-slate-300 transition hover:bg-slate-800 hover:text-white"
                  >
                    Login
                  </Link>
                </>
              )}

            </div>

          </div>

        </section>

        {/* Features */}
        <section className="border-y border-slate-800 bg-slate-900/50">

          <div className="mx-auto grid max-w-7xl gap-6 px-6 py-16 md:grid-cols-3">

            <div className="rounded-2xl border border-slate-800 bg-slate-900 p-6">

              <div className="mb-4 text-3xl">
                🎯
              </div>

              <h2 className="text-xl font-semibold">
                Personalized
              </h2>

              <p className="mt-3 text-sm leading-6 text-slate-400">
                Recommendations are generated
                from your movie ratings and
                preferences.
              </p>

            </div>

            <div className="rounded-2xl border border-slate-800 bg-slate-900 p-6">

              <div className="mb-4 text-3xl">
                🤖
              </div>

              <h2 className="text-xl font-semibold">
                AI Powered
              </h2>

              <p className="mt-3 text-sm leading-6 text-slate-400">
                Uses TF-IDF, cosine similarity,
                popularity scoring and hybrid
                recommendation techniques.
              </p>

            </div>

            <div className="rounded-2xl border border-slate-800 bg-slate-900 p-6">

              <div className="mb-4 text-3xl">
                💡
              </div>

              <h2 className="text-xl font-semibold">
                Explainable
              </h2>

              <p className="mt-3 text-sm leading-6 text-slate-400">
                Understand why a movie was
                recommended based on your
                preferences.
              </p>

            </div>

          </div>

        </section>

        {/* User section */}
        {isAuthenticated && (
          <section className="mx-auto max-w-7xl px-6 py-16">

            <div className="rounded-2xl border border-slate-800 bg-slate-900 p-8">

              <p className="text-sm text-slate-400">
                Welcome back
              </p>

              <h2 className="mt-2 text-2xl font-bold">
                {user?.name || user?.email}
              </h2>

              <p className="mt-2 text-slate-400">
                Your personalized movie
                recommendations are waiting.
              </p>

              <Link
                to="/recommendations"
                className="mt-6 inline-block rounded-lg bg-blue-600 px-5 py-3 font-medium transition hover:bg-blue-700"
              >
                View Recommendations
              </Link>

            </div>

          </section>
        )}

      </main>

      {/* Footer */}
      <footer className="border-t border-slate-800">

        <div className="mx-auto max-w-7xl px-6 py-8 text-center text-sm text-slate-500">

          MovieAI — AI-powered movie
          recommendation system

        </div>

      </footer>

    </div>
  );
}

export default Home;