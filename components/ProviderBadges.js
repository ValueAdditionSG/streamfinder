// components/ProviderBadges.js
import Image from 'next/image'
import { JUSTWATCH_FALLBACK } from './CountrySelector'

function ProviderLogo({ provider }) {
  return (
    <div className="flex flex-col items-center gap-1 group">
      <div className="w-10 h-10 rounded-lg overflow-hidden bg-gray-800 border border-gray-700 flex items-center justify-center">
        {provider.logo ? (
          <Image
            src={provider.logo}
            alt={provider.name}
            width={40}
            height={40}
            className="w-full h-full object-cover"
          />
        ) : (
          <span className="text-xs text-gray-400 text-center leading-tight px-1">
            {provider.name.slice(0, 2)}
          </span>
        )}
      </div>
      <span className="text-xs text-gray-400 text-center leading-tight max-w-[56px] truncate">
        {provider.name}
      </span>
    </div>
  )
}

function Section({ label, providers, colorClass }) {
  if (!providers || providers.length === 0) return null
  return (
    <div className="mb-3">
      <span className={`badge ${colorClass} mb-2`}>{label}</span>
      <div className="flex flex-wrap gap-3 mt-2">
        {providers.map((p) => (
          <ProviderLogo key={p.id} provider={p} />
        ))}
      </div>
    </div>
  )
}

export default function ProviderBadges({ data, loading, country, title }) {
  if (loading) {
    return (
      <div className="mt-3 animate-pulse">
        <div className="h-3 w-24 bg-gray-700 rounded mb-2" />
        <div className="flex gap-2">
          {[1, 2, 3].map((i) => (
            <div key={i} className="w-10 h-10 rounded-lg bg-gray-700" />
          ))}
        </div>
      </div>
    )
  }

  if (!data) return null

  if (!data.available) {
    const fallbackBase = JUSTWATCH_FALLBACK[country]
    if (fallbackBase && title) {
      return (
        <div className="mt-3">
          <p className="text-sm text-gray-400 mb-2">
            Streaming data for this country isn&apos;t in our database yet.
          </p>
          <a
            href={`${fallbackBase}${encodeURIComponent(title)}`}
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center gap-1.5 text-sm font-medium text-brand-500 hover:text-brand-400"
          >
            🔍 Search on JustWatch Vietnam →
          </a>
        </div>
      )
    }
    return (
      <p className="text-sm text-gray-500 mt-3 italic">
        Not available for streaming in this country.
      </p>
    )
  }

  const { providers, link } = data
  const hasAny =
    providers.flatrate?.length ||
    providers.rent?.length ||
    providers.buy?.length ||
    providers.free?.length ||
    providers.ads?.length

  if (!hasAny) {
    return (
      <p className="text-sm text-gray-500 mt-3 italic">
        No streaming options found for this country.
      </p>
    )
  }

  return (
    <div className="mt-3">
      <Section label="Subscription" providers={providers.flatrate} colorClass="badge-flatrate" />
      <Section label="Free" providers={[...(providers.free || []), ...(providers.ads || [])]} colorClass="badge-free" />
      <Section label="Rent" providers={providers.rent} colorClass="badge-rent" />
      <Section label="Buy" providers={providers.buy} colorClass="badge-buy" />
      {link && (
        <a
          href={link}
          target="_blank"
          rel="noopener noreferrer"
          className="text-xs text-brand-500 hover:text-brand-400 mt-1 inline-block"
        >
          View on JustWatch →
        </a>
      )}
    </div>
  )
}
