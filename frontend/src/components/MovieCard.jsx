import { Link } from "react-router-dom";

function MovieCard({ movie }) {
  return (
    <Link to={`/movie/${movie.movieId}`} className="group block">
      <div className="overflow-hidden rounded-xl border border-slate-800 bg-slate-900 transition duration-300 hover:-translate-y-1 hover:border-blue-500/50 hover:shadow-lg hover:shadow-blue-500/10">
        {/* Poster */}
        <div className="relative aspect-[2/3] overflow-hidden bg-slate-800">
          {movie.posterUrl ? (
            <img
              src={movie.posterUrl}
              alt={movie.title}
              className="h-full w-full object-cover transition duration-500 group-hover:scale-105"
            />
          ) : (
            <div className="flex h-full items-center justify-center p-4 text-center">
              <span className="text-sm text-slate-500">No Poster</span>
            </div>
          )}

          {/* Score */}
          {movie.recommendation_score !== undefined && (
            <div className="absolute right-2 top-2 rounded-lg bg-blue-600 px-2 py-1 text-xs font-bold">
              {(movie.recommendation_score * 100).toFixed(0)}%
            </div>
          )}

          {movie.averageRating && (
            <div className="absolute bottom-2 left-2 rounded-md bg-black/80 px-2 py-1 text-xs text-white">
              ⭐ {Number(movie.averageRating).toFixed(1)}
            </div>
          )}
        </div>

        {/* Information */}
        <div className="p-4">
          <h3 className="line-clamp-1 font-semibold text-white group-hover:text-blue-400">
            {movie.title}
          </h3>

          {movie.genres && (
            <p className="mt-1 line-clamp-1 text-xs text-slate-500">
              {movie.genres.replace(/\|/g, " • ")}
            </p>
          )}
        </div>
      </div>
    </Link>
  );
}

export default MovieCard;
