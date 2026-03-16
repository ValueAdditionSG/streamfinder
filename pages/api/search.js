// pages/api/search.js
// Searches TMDB for movies and TV shows matching a query

const TMDB_BASE = 'https://api.themoviedb.org/3'

export default async function handler(req, res) {
  const { query, page = 1 } = req.query

  if (!query || query.trim().length < 2) {
    return res.status(400).json({ error: 'Query too short' })
  }

  const apiKey = process.env.TMDB_API_KEY
  if (!apiKey) {
    return res.status(500).json({ error: 'TMDB API key not configured' })
  }

  try {
    const response = await fetch(
      `${TMDB_BASE}/search/multi?api_key=${apiKey}&query=${encodeURIComponent(query)}&page=${page}&include_adult=false`
    )

    if (!response.ok) {
      throw new Error(`TMDB error: ${response.status}`)
    }

    const data = await response.json()

    // Filter to only movies and TV shows (exclude people)
    const results = data.results
      .filter((item) => item.media_type === 'movie' || item.media_type === 'tv')
      .map((item) => ({
        id: item.id,
        mediaType: item.media_type,
        title: item.title || item.name,
        originalTitle: item.original_title || item.original_name,
        overview: item.overview,
        posterPath: item.poster_path,
        backdropPath: item.backdrop_path,
        releaseDate: item.release_date || item.first_air_date,
        voteAverage: item.vote_average,
        popularity: item.popularity,
      }))

    return res.status(200).json({
      results,
      totalResults: data.total_results,
      totalPages: data.total_pages,
      page: data.page,
    })
  } catch (err) {
    console.error('Search error:', err)
    return res.status(500).json({ error: 'Failed to search' })
  }
}
