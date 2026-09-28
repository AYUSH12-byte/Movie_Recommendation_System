import MovieCard from "./MovieCard";

function MovieGrid({
  movies = [],
  loading = false,
  emptyMessage = "No movies found.",
}) {
  if (loading) {
    return (
      <div className="grid grid-cols-2 gap-4 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 xl:grid-cols-6">
        {Array.from({ length: 6 }).map((_, index) => (
          <div
            key={index}
            className="animate-pulse overflow-hidden rounded-xl border border-slate-800 bg-slate-900"
          >
            <div className="aspect-[2/3] bg-slate-800" />

            <div className="space-y-2 p-4">
              <div className="h-4 rounded bg-slate-800" />
              <div className="h-3 w-2/3 rounded bg-slate-800" />
            </div>
          </div>
        ))}
      </div>
    );
  }

  if (!movies.length) {
    return (
      <div className="rounded-xl border border-dashed border-slate-700 bg-slate-900/50 px-6 py-12 text-center">
        <p className="text-slate-400">{emptyMessage}</p>
      </div>
    );
  }

  return (
    <div className="grid grid-cols-2 gap-4 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 xl:grid-cols-6">
      {movies.map((movie) => (
        <MovieCard key={movie.movieId} movie={movie} />
      ))}
    </div>
  );
}

export default MovieGrid;
