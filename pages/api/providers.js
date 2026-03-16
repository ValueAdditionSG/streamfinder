// pages/api/providers.js
// Returns streaming availability for a given movie/show in a given country

const TMDB_BASE = 'https://api.themoviedb.org/3'

export default async function handler(req, res) {
  const { id, mediaType, country = 'SG' } = req.query

  if (!id || !mediaType) {
    return res.status(400).json({ error: 'id and mediaType are required' })
  }

  const apiKey = process.env.TMDB_API_KEY
  if (!apiKey) {
    return res.status(500).json({ error: 'TMDB API key not configured' })
  }

  try {
    const endpoint = mediaType === 'movie'
      ? `${TMDB_BASE}/movie/${id}/watch/providers?api_key=${apiKey}`
      : `${TMDB_BASE}/tv/${id}/watch/providers?api_key=${apiKey}`

    const response = await fetch(endpoint)

    if (!response.ok) {
      throw new Error(`TMDB error: ${response.status}`)
    }

    const data = await response.json()
    const countryData = data.results?.[country.toUpperCase()] || null

    if (!countryData) {
      return res.status(200).json({
        country,
        available: false,
        providers: null,
        link: null,
      })
    }

    const normalize = (list) =>
      (list || []).map((p) => ({
        id: p.provider_id,
        name: p.provider_name,
        logo: p.logo_path
          ? `https://image.tmdb.org/t/p/original${p.logo_path}`
          : null,
        displayPriority: p.display_priority,
      }))

    return res.status(200).json({
      country,
      available: true,
      link: countryData.link,
      providers: {
        flatrate: normalize(countryData.flatrate), // Subscription (Netflix, etc.)
        rent: normalize(countryData.rent),         // Rent (iTunes, etc.)
        buy: normalize(countryData.buy),           // Buy
        free: normalize(countryData.free),         // Free (with ads)
        ads: normalize(countryData.ads),           // Ad-supported
      },
    })
  } catch (err) {
    console.error('Providers error:', err)
    return res.status(500).json({ error: 'Failed to fetch providers' })
  }
}
