import { FaSearch } from 'react-icons/fa'

export default function SearchBar({ query, setQuery, onSearch, loading }) {
  const handleSubmit = (e) => {
    e.preventDefault()
    if (query.trim()) onSearch()
  }

  return (
    <form onSubmit={handleSubmit} className="w-full max-w-2xl mx-auto">
      <div className="relative flex items-center">
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="What do you want to learn? (e.g., Learn LangChain)"
          className="w-full px-5 py-3.5 pr-14 rounded-xl bg-dark border border-gray-700 
                     text-white placeholder-gray-500 focus:outline-none focus:border-primary 
                     focus:ring-1 focus:ring-primary/50 transition-all text-sm"
        />
        <button
          type="submit"
          disabled={loading || !query.trim()}
          className="absolute right-2 p-2.5 rounded-lg bg-primary hover:bg-primary/80 
                     disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
        >
          {loading ? (
            <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
          ) : (
            <FaSearch className="text-white text-sm" />
          )}
        </button>
      </div>
    </form>
  )
}
