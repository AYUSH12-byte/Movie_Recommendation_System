import { useState } from "react";
import { useNavigate } from "react-router-dom";

import api from "../services/api";

function MovieSearch() {
  const navigate = useNavigate();

  const [query, setQuery] = useState("");
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [searched, setSearched] = useState(false);

  const handleSearch = async (e) => {
    e.preventDefault();

    const searchTerm = query.trim();

    if (!searchTerm) {
      setResults([]);
      setSearched(false);
      return;
    }

    try {
      setLoading(true);
      setSearched(true);

      const response = await api.get(
        `/movies/search/query?q=${encodeURIComponent(searchTerm)}`,
      );

      const data = response.data;

      setResults(data.movies || data.results || data || []);
    } catch (error) {
      console.error("Movie search failed:", error);

      setResults([]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="mb-12">
      {/* Search Form */}
      <form onSubmit={handleSearch} className="mx-auto flex max-w-3xl gap-3">
        <div className="relative flex-1">
          <span className="pointer-events-none absolute left-4 top-1/2 -translate-y-1/2 text-slate-500">
            🔍
          </span>

          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Search for a movie..."
            className="w-full rounded-xl border border-slate-700 bg-slate-900 py-4 pl-12 pr-4 text-white outline-none transition placeholder:text-slate-500 focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20"
          />
        </div>

        <button
          type="submit"
          disabled={loading}
          className="rounded-xl bg-blue-600 px-6 font-semibold transition hover:bg-blue-700 disabled:opacity-60"
        >
          {loading ? "Searching..." : "Search"}
        </button>
      </form>

      {/* Results */}
      {searched && (
        <div className="mt-8">
          <h2 className="mb-5 text-xl font-bold">Search Results</h2>

          {loading ? (
            <div className="py-10 text-center text-slate-500">
              Searching movies...
            </div>
          ) : results.length === 0 ? (
            <div className="rounded-xl border border-dashed border-slate-700 bg-slate-900/50 px-6 py-10 text-center">
              <p className="text-slate-400">No movies found for "{query}".</p>
            </div>
          ) : (
            <div className="grid grid-cols-2 gap-4 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 xl:grid-cols-6">
              {results.map((movie) => (
                <button
                  key={movie.movieId}
                  onClick={() => navigate(`/movie/${movie.movieId}`)}
                  className="group overflow-hidden rounded-xl border border-slate-800 bg-slate-900 text-left transition hover:-translate-y-1 hover:border-blue-500/50"
                >
                  <div className="aspect-[2/3] bg-slate-800">
                    {movie.posterUrl ? (
                      <img
                        src={movie.posterUrl}
                        alt={movie.title}
                        className="h-full w-full object-cover transition duration-500 group-hover:scale-105"
                      />
                    ) : (
                      <div className="flex h-full items-center justify-center p-4 text-center">
                        <span className="text-sm text-slate-500">🎬</span>
                      </div>
                    )}
                  </div>

                  <div className="p-3">
                    <h3 className="line-clamp-2 font-semibold text-white group-hover:text-blue-400">
                      {movie.title}
                    </h3>

                    {movie.genres && (
                      <p className="mt-1 line-clamp-1 text-xs text-slate-500">
                        {movie.genres.replace(/\|/g, " • ")}
                      </p>
                    )}
                  </div>
                </button>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
}

export default MovieSearch;
