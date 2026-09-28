import { Link } from "react-router-dom";

function MovieCard({ movie }) {
  const recommendationScore =
    movie.recommendation_score ??
    movie.recommendationScore;

  const poster =
    movie.posterUrl ||
    movie.poster_url ||
    movie.poster ||
    null;

  console.log("MOVIE CARD:", movie.title, {
    posterUrl: movie.posterUrl,
    poster_url: movie.poster_url,
    poster: movie.poster,
  });

  return (
    <Link
      to={`/movie/${movie.movieId}`}
      className="group block"
    >
      <div className="overflow-hidden rounded-xl border border-slate-800 bg-slate-900 transition duration-300 hover:-translate-y-1 hover:border-blue-500/50 hover:shadow-xl hover:shadow-blue-500/10">

        {/* Poster */}
        <div className="relative aspect-[2/3] overflow-hidden bg-slate-800">

          {poster ? (
            <img
              src={poster}
              alt={movie.title}
              loading="lazy"
              className="h-full w-full object-cover transition duration-500 group-hover:scale-110"
              onError={(event) => {
                console.error(
                  "POSTER FAILED:",
                  movie.title,
                  poster
                );

                event.currentTarget.style.display = "none";
              }}
            />
          ) : (
            <div className="flex h-full flex-col items-center justify-center gap-2 text-center">
              <span className="text-4xl">
                🎬
              </span>

              <span className="px-3 text-xs text-slate-500">
                No poster available
              </span>
            </div>
          )}

          {/* Recommendation Score */}
          {recommendationScore !== undefined &&
            recommendationScore !== null && (
              <div className="absolute right-2 top-2 rounded-lg border border-blue-400/20 bg-blue-600/90 px-2 py-1 text-xs font-bold text-white shadow-lg backdrop-blur">
                {(Number(recommendationScore) * 100).toFixed(0)}%
              </div>
            )}

          {/* Rating */}
          {movie.averageRating !== undefined &&
            movie.averageRating !== null && (
              <div className="absolute bottom-2 left-2 rounded-md bg-black/80 px-2 py-1 text-xs font-medium text-white backdrop-blur">
                ⭐{" "}
                {Number(movie.averageRating).toFixed(1)}
              </div>
            )}
        </div>

        {/* Movie Info */}
        <div className="p-4">
          <h3 className="line-clamp-2 min-h-[40px] font-semibold leading-5 text-white transition group-hover:text-blue-400">
            {movie.title}
          </h3>

          {movie.genres && (
            <p className="mt-2 line-clamp-1 text-xs text-slate-500">
              {movie.genres.replace(/\|/g, " • ")}
            </p>
          )}
        </div>
      </div>
    </Link>
  );
}

export default MovieCard;