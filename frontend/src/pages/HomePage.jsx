import { useState } from 'react'
import toast from 'react-hot-toast'
import { FaBrain, FaYoutube } from 'react-icons/fa'
import SearchBar from '../components/SearchBar'
import VideoCard from '../components/VideoCard'
import LoadingSpinner from '../components/LoadingSpinner'
import { searchVideos } from '../services/api'

export default function HomePage() {
  // State
  const [query, setQuery] = useState('')
  const [videos, setVideos] = useState([])
  const [loading, setLoading] = useState(false)
  const [searched, setSearched] = useState(false)

  // Search handler
  const handleSearch = async () => {
    setLoading(true)
    setSearched(true)
    
    try {
      const { data } = await searchVideos(query)
      setVideos(data.videos)
      
      if (data.videos.length === 0) {
        toast('No videos found. Try a different query.', { icon: '🔍' })
      }
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Search failed. Check your API key.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div>
      {/* Hero Section */}
      <div className="text-center py-12">
        <div className="flex items-center justify-center gap-3 mb-4">
          <FaBrain className="text-primary text-4xl" />
          <h1 className="text-4xl font-bold">
            <span className="text-primary">Tube</span>
            <span className="text-white">Mentor</span>
            <span className="text-primary/50 ml-2 text-lg">AI</span>
          </h1>
        </div>
        
        <p className="text-gray-400 max-w-xl mx-auto mb-8">
          Search any YouTube video, get AI-powered summaries, quizzes, and downloadable PDF notes — all in one place.
        </p>
        
        <SearchBar query={query} setQuery={setQuery} onSearch={handleSearch} loading={loading} />
      </div>

      {/* Loading State */}
      {loading && <LoadingSpinner text="Searching YouTube..." />}

      {/* Results Grid */}
      {!loading && videos.length > 0 && (
        <div>
          <div className="flex items-center gap-2 mb-4">
            <FaYoutube className="text-red-500" />
            <h2 className="text-lg font-semibold text-white">
              Results for "<span className="text-primary">{query}</span>"
            </h2>
            <span className="text-xs text-gray-500">({videos.length} videos)</span>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
            {videos.map((v) => (
              <VideoCard key={v.video_id} video={v} />
            ))}
          </div>
        </div>
      )}

      {/* No Results */}
      {!loading && searched && videos.length === 0 && (
        <p className="text-center text-gray-500 mt-8">No results found. Try a different search term.</p>
      )}
    </div>
  )
}
