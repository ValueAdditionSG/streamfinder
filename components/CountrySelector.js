// components/CountrySelector.js
const COUNTRIES = [
  { code: 'SG', name: '🇸🇬 Singapore' },
  { code: 'US', name: '🇺🇸 United States' },
  { code: 'GB', name: '🇬🇧 United Kingdom' },
  { code: 'AU', name: '🇦🇺 Australia' },
  { code: 'IN', name: '🇮🇳 India' },
  { code: 'CA', name: '🇨🇦 Canada' },
  { code: 'DE', name: '🇩🇪 Germany' },
  { code: 'FR', name: '🇫🇷 France' },
  { code: 'JP', name: '🇯🇵 Japan' },
  { code: 'KR', name: '🇰🇷 South Korea' },
  { code: 'MY', name: '🇲🇾 Malaysia' },
  { code: 'ID', name: '🇮🇩 Indonesia' },
  { code: 'TH', name: '🇹🇭 Thailand' },
  { code: 'PH', name: '🇵🇭 Philippines' },
  { code: 'NZ', name: '🇳🇿 New Zealand' },
  { code: 'ZA', name: '🇿🇦 South Africa' },
  { code: 'BR', name: '🇧🇷 Brazil' },
  { code: 'MX', name: '🇲🇽 Mexico' },
  { code: 'ES', name: '🇪🇸 Spain' },
  { code: 'IT', name: '🇮🇹 Italy' },
  { code: 'NL', name: '🇳🇱 Netherlands' },
  { code: 'SE', name: '🇸🇪 Sweden' },
  { code: 'NO', name: '🇳🇴 Norway' },
  { code: 'AE', name: '🇦🇪 UAE' },
  { code: 'VN', name: '🇻🇳 Vietnam' },
]

export default function CountrySelector({ value, onChange }) {
  return (
    <select
      value={value}
      onChange={(e) => onChange(e.target.value)}
      className="bg-gray-800 border border-gray-700 text-white rounded-xl px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-brand-500 cursor-pointer"
    >
      {COUNTRIES.map((c) => (
        <option key={c.code} value={c.code}>
          {c.name}
        </option>
      ))}
    </select>
  )
}

export { COUNTRIES }
