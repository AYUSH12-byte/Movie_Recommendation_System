function MovieDetails({
  movie,
  poster,
  backdrop,
  genres,
}) {
  return (
    <section className="relative overflow-hidden">
      {/* Backdrop */}
      {backdrop && (
        <div className="absolute inset-0">
          <img
            src={backdrop}
            alt=""
            className="h-full w-full object-cover opacity-20"
          />

          <div className="absolute inset-0 bg-gradient-to-b from-slate-950/40 via-slate-950/80 to-slate-950" />
        </div>
      )}

      <div className="relative mx-auto max-w-7xl px-6 py-8">
        <div className="grid gap-10 md:grid-cols-[280px_1fr]">
          {/* Poster */}
          <div className="overflow-hidden rounded-2xl border border-slate-800 bg-slate-900 shadow-2xl">
            {poster ? (
              <img
                src={poster}
                alt={movie.title}
                className="aspect-[2/3] h-full w-full object-cover"
              />
            ) : (
              <div className="flex aspect-[2/3] flex-col items-center justify-center gap-3 text-slate-500">
                <span className="text-6xl">
                  🎬
                </span>

                <span>
                  No poster available
                </span>
              </div>
            )}
          </div>

          {/* Movie Information */}
          <div className="flex flex-col justify-center">
            <MovieTitle movie={movie} />

            <MovieGenres genres={genres} />

            <MovieStats movie={movie} />

            <MovieOverview movie={movie} />
          </div>
        </div>
      </div>
    </section>
  );
}


/* ==========================================================
   TITLE
========================================================== */

function MovieTitle({ movie }) {
  return (
    <h1 className="text-4xl font-extrabold tracking-tight text-white sm:text-5xl">
      {movie.title}
    </h1>
  );
}


/* ==========================================================
   GENRES
========================================================== */

function MovieGenres({ genres }) {
  if (!genres?.length) {
    return null;
  }

  return (
    <div className="mt-5 flex flex-wrap gap-2">
      {genres.map((genre) => (
        <span
          key={genre}
          className="rounded-full border border-slate-700 bg-slate-900/80 px-3 py-1 text-sm text-slate-300"
        >
          {genre}
        </span>
      ))}
    </div>
  );
}


/* ==========================================================
   MOVIE STATS
========================================================== */

function MovieStats({ movie }) {
  const averageRating =
    movie.averageRating ??
    movie.communityRating ??
    null;

  const ratingCount =
    movie.totalRatings ??
    movie.ratingCount ??
    null;

  const tmdbRating =
    movie.tmdbRating ??
    null;

  const releaseDate =
    movie.releaseDate ||
    null;

  return (
    <>
      <div className="mt-6 flex flex-wrap gap-4">
        {averageRating !== null && (
          <StatCard
            label="Community Rating"
            value={`⭐ ${Number(
              averageRating
            ).toFixed(1)}/5`}
          />
        )}

        {ratingCount !== null && (
          <StatCard
            label="Ratings"
            value={ratingCount}
          />
        )}

        {tmdbRating !== null && (
          <StatCard
            label="TMDB Rating"
            value={`⭐ ${Number(
              tmdbRating
            ).toFixed(1)}`}
          />
        )}
      </div>

      {releaseDate && (
        <p className="mt-5 text-sm text-slate-400">
          Release Date:{" "}
          <span className="font-medium text-slate-200">
            {releaseDate}
          </span>
        </p>
      )}
    </>
  );
}


/* ==========================================================
   STAT CARD
========================================================== */

function StatCard({
  label,
  value,
}) {
  return (
    <div className="rounded-xl border border-slate-800 bg-slate-900/80 px-4 py-3">
      <div className="text-xs text-slate-500">
        {label}
      </div>

      <div className="mt-1 text-lg font-bold text-white">
        {value}
      </div>
    </div>
  );
}


/* ==========================================================
   OVERVIEW
========================================================== */

function MovieOverview({ movie }) {
  if (!movie.overview) {
    return null;
  }

  return (
    <div className="mt-7 max-w-3xl">
      <h2 className="text-xl font-bold text-white">
        Overview
      </h2>

      <p className="mt-3 leading-7 text-slate-400">
        {movie.overview}
      </p>
    </div>
  );
}


export default MovieDetails;