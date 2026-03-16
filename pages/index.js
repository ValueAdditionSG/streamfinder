// pages/index.js
import { useState, useRef, useCallback } from 'react'
import Head from 'next/head'
import ResultCard from '../components/ResultCard'
import CountrySelector from '../components/CountrySelector'

export default function Home() {
  const [query, setQuery] = useState('')
  const [country, setCountry] = useState('SG')
  const [results, setResults] = useState([])
  const [loading, setLoading] = useState(false)
  const [searched, setSearched] = useState(false)
  const [error, setError] = useState(null)
  const inputRef = useRef(null)
  const debounceRef = useRef(null)

  const search = useCallback(async (q, ct) => {
    if (!q || q.trim().length < 2) {
      setResults([])
      setSearched(false)
      return
    }
    setLoading(true)
    setError(null)
    try {
      const res = await fetch(`/api/search?query=${encodeURIComponent(q)}`)
      const data = await res.json()
      if (!res.ok) throw new Error(data.error || 'Search failed')
      setResults(data.results || [])
      setSearched(true)
    } catch (e) {
      setError(e.message)
    } finally {
      setLoading(false)
    }
  }, [])

  const handleInput = (e) => {
    const val = e.target.value
    setQuery(val)
    clearTimeout(debounceRef.current)
    debounceRef.current = setTimeout(() => search(val, country), 400)
  }

  const handleSubmit = (e) => {
    e.preventDefault()
    clearTimeout(debounceRef.current)
    search(query, country)
  }

  return (
    <>
      <Head>
        <title>StreamFinder — Where to Watch Movies &amp; TV</title>
        <meta name="description" content="Find which streaming service has your movie or TV show." />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <link rel="icon" href="/favicon.ico" />
      </Head>

      <main className="min-h-screen bg-gray-950 px-4 py-12">
        <div className="max-w-2xl mx-auto">

          {/* Header */}
          <div className="text-center mb-10">
            <h1 className="text-4xl font-bold text-white mb-2">
              🎬 StreamFinder
            </h1>
            <p className="text-gray-400 text-lg">
              Find where to watch any movie or TV show
            </p>
          </div>

          {/* Search form */}
          <form onSubmit={handleSubmit} className="flex flex-col sm:flex-row gap-3 mb-8">
            <div className="relative flex-1">
              <span className="absolute left-4 top-1/2 -translate-y-1/2 text-gray-500 text-lg">
                🔍
              </span>
              <input
                ref={inputRef}
                type="text"
                value={query}
                onChange={handleInput}
                placeholder="Search movies or TV shows..."
                className="w-full bg-gray-800 border border-gray-700 text-white placeholder-gray-500 rounded-xl pl-11 pr-4 py-3 text-base focus:outline-none focus:ring-2 focus:ring-brand-500 focus:border-transparent"
                autoFocus
              />
            </div>
            <CountrySelector value={country} onChange={setCountry} />
          </form>

          {/* Loading */}
          {loading && (
            <div className="text-center py-12 text-gray-500">
              <div className="animate-spin text-4xl mb-3">⏳</div>
              Searching...
            </div>
          )}

          {/* Error */}
          {error && !loading && (
            <div className="text-center py-8 text-red-400">
              ⚠️ {error}
            </div>
          )}

          {/* No results */}
          {!loading && searched && results.length === 0 && !error && (
            <div className="text-center py-12 text-gray-500">
              <div className="text-5xl mb-4">🤷</div>
              <p>No results found for &ldquo;{query}&rdquo;</p>
            </div>
          )}

          {/* Results */}
          {!loading && results.length > 0 && (
            <div className="flex flex-col gap-4">
              <p className="text-sm text-gray-500">
                {results.length} result{results.length !== 1 ? 's' : ''} — click any title to see where to watch
              </p>
              {results.map((item) => (
                <ResultCard key={`${item.mediaType}-${item.id}`} item={item} country={country} />
              ))}
            </div>
          )}

          {/* Empty state */}
          {!loading && !searched && (
            <div className="text-center py-16 text-gray-600">
              <div className="text-6xl mb-4">🍿</div>
              <p className="text-lg">Start typing to find your movie or show</p>
            </div>
          )}

        </div>

        {/* Footer */}
        <footer className="text-center mt-16 text-gray-700 text-xs">
          Streaming data powered by{' '}
          <a href="https://www.themoviedb.org" target="_blank" rel="noopener noreferrer" className="underline hover:text-gray-500">
            TMDB
          </a>
          {' '}·{' '}
          <a href="https://www.justwatch.com" target="_blank" rel="noopener noreferrer" className="underline hover:text-gray-500">
            JustWatch
          </a>
        </footer>
      </main>
    </>
  )
}
