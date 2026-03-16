// components/ResultCard.js
import Image from 'next/image'
import { useState, useEffect } from 'react'
import ProviderBadges from './ProviderBadges'

export default function ResultCard({ item, country }) {
  const [providerData, setProviderData] = useState(null)
  const [loading, setLoading] = useState(false)
  const [expanded, setExpanded] = useState(false)

  const year = item.releaseDate ? item.releaseDate.slice(0, 4) : '—'
  const rating = item.voteAverage ? item.voteAverage.toFixed(1) : null
  const typeLabel = item.mediaType === 'movie' ? 'Movie' : 'TV Series'

  const fetchProviders = async () => {
    if (providerData !== null) return
    setLoading(true)
    try {
      const res = await fetch(
        `/api/providers?id=${item.id}&mediaType=${item.mediaType}&country=${country}`
      )
      const data = await res.json()
      setProviderData(data)
    } catch (e) {
      setProviderData({ available: false })
    } finally {
      setLoading(false)
    }
  }

  const toggle = () => {
    if (!expanded) fetchProviders()
    setExpanded((v) => !v)
  }

  // Re-fetch if country changes and card is already expanded
  useEffect(() => {
    if (expanded) {
      setProviderData(null)
      fetchProviders()
    }
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [country])

  return (
    <div className="bg-gray-900 border border-gray-800 rounded-2xl overflow-hidden hover:border-gray-600 transition-colors">
      <div className="flex gap-4 p-4">
        {/* Poster */}
        <div className="flex-shrink-0 w-16 h-24 rounded-xl overflow-hidden bg-gray-800">
          {item.posterPath ? (
            <Image
              src={`https://image.tmdb.org/t/p/w154${item.posterPath}`}
              alt={item.title}
              width={64}
              height={96}
              className="w-full h-full object-cover"
            />
          ) : (
            <div className="w-full h-full flex items-center justify-center text-gray-600 text-3xl">
              🎬
            </div>
          )}
        </div>

        {/* Info */}
        <div className="flex-1 min-w-0">
          <div className="flex items-start justify-between gap-2">
            <div>
              <h3 className="font-semibold text-white leading-tight">{item.title}</h3>
              <div className="flex items-center gap-2 mt-1 flex-wrap">
                <span className="text-xs text-gray-500 bg-gray-800 px-2 py-0.5 rounded-full">
                  {typeLabel}
                </span>
                <span className="text-xs text-gray-500">{year}</span>
                {rating && rating !== '0.0' && (
                  <span className="text-xs text-yellow-400">★ {rating}</span>
                )}
              </div>
            </div>
          </div>

          {item.overview && (
            <p className="text-sm text-gray-400 mt-2 line-clamp-2 leading-relaxed">
              {item.overview}
            </p>
          )}

          <button
            onClick={toggle}
            className="mt-3 text-sm text-brand-500 hover:text-brand-400 font-medium transition-colors"
          >
            {expanded ? 'Hide streaming ▲' : 'Where to watch ▼'}
          </button>
        </div>
      </div>

      {expanded && (
        <div className="px-4 pb-4 border-t border-gray-800 pt-3">
          <ProviderBadges data={providerData} loading={loading} />
        </div>
      )}
    </div>
  )
}
