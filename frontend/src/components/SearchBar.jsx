import { FaSearch } from 'react-icons/fa'

export default function SearchBar({ query, setQuery, onSearch, loading }) {
  const handleSubmit = (e) => {
    e.preventDefault()
    if (query.trim()) onSearch()
  }

  return (
    <form onSubmit={handleSubmit} className="w-full max-w-2xl mx-auto">
      <div className="relative flex items-center group">
        {/* Glow effect */}
        <div className="absolute -inset-1 bg-gradient-to-r from-cyan-500/20 to-purple-500/20 rounded-2xl blur-lg 
                      opacity-0 group-hover:opacity-100 group-focus-within:opacity-100 transition-opacity" />
        
        <div className="relative w-full flex items-center">
          <FaSearch className="absolute left-5 text-gray-500 group-focus-within:text-cyan-400 transition-colors" />
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="What do you want to learn? (e.g., Python, Machine Learning)"
            className="w-full px-5 py-4 pl-12 pr-32 rounded-xl bg-secondary/80 backdrop-blur-sm
                       border border-gray-700 text-white placeholder-gray-500 
                       focus:outline-none focus:border-cyan-500/50 focus:ring-2 focus:ring-cyan-500/20 
                       transition-all duration-300 text-sm"
          />
          <button
            type="submit"
            disabled={loading || !query.trim()}
            className="absolute right-2 px-5 py-2.5 rounded-lg font-medium text-sm
                       bg-gradient-to-r from-cyan-500 to-purple-500 text-white
                       hover:from-cyan-400 hover:to-purple-400 hover:scale-105
                       disabled:opacity-40 disabled:cursor-not-allowed disabled:hover:scale-100
                       transition-all duration-300 flex items-center gap-2 shadow-lg shadow-cyan-500/25"
          >
            {loading ? (
              <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
            ) : (
              <>
                <FaSearch className="text-xs" />
                <span>Search</span>
              </>
            )}
          </button>
        </div>
      </div>
    </form>
  )
}
