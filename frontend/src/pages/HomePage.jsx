import { useState } from 'react'
import toast from 'react-hot-toast'
import { FaBrain, FaYoutube, FaRocket, FaMagic, FaFileAlt, FaQuestionCircle } from 'react-icons/fa'
import { HiSparkles } from 'react-icons/hi'
import SearchBar from '../components/SearchBar'
import VideoCard from '../components/VideoCard'
import LoadingSpinner from '../components/LoadingSpinner'
import { searchVideos } from '../services/api'

const features = [
  { icon: FaMagic, label: 'AI Summaries', color: 'from-cyan-400 to-blue-500' },
  { icon: FaQuestionCircle, label: 'Smart Quizzes', color: 'from-purple-400 to-pink-500' },
  { icon: FaFileAlt, label: 'PDF Notes', color: 'from-emerald-400 to-cyan-500' },
]

export default function HomePage() {
  const [query, setQuery] = useState('')
  const [videos, setVideos] = useState([])
  const [loading, setLoading] = useState(false)
  const [searched, setSearched] = useState(false)

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
    <div className="relative min-h-[calc(100vh-4rem)] overflow-hidden">
      {/* Animated Background */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-20 -left-32 w-96 h-96 bg-cyan-500/10 rounded-full blur-3xl animate-float" />
        <div className="absolute bottom-20 -right-32 w-96 h-96 bg-purple-500/10 rounded-full blur-3xl animate-float" style={{ animationDelay: '2s' }} />
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[800px] h-[800px] bg-gradient-radial from-cyan-500/5 to-transparent rounded-full" />
      </div>

      <div className="max-w-7xl mx-auto px-4 py-6 relative">
        {/* Hero Section */}
        <div className="text-center py-16 animate-fade-in">
          {/* Logo */}
          <div className="flex items-center justify-center gap-3 mb-6 animate-bounce-in">
            <div className="relative">
              <FaBrain className="text-cyan-400 text-5xl animate-pulse" />
              <div className="absolute -inset-2 bg-cyan-400/20 rounded-full blur-lg" />
            </div>
            <h1 className="text-5xl md:text-6xl font-bold">
              <span className="bg-gradient-to-r from-cyan-400 to-cyan-300 bg-clip-text text-transparent">Tube</span>
              <span className="text-white">Mentor</span>
              <span className="bg-gradient-to-r from-purple-400 to-pink-400 bg-clip-text text-transparent ml-2 text-2xl">AI</span>
            </h1>
          </div>
          
          <p className="text-gray-400 text-lg max-w-2xl mx-auto mb-4 animate-fade-in-up" style={{ animationDelay: '0.2s' }}>
            Transform any YouTube video into a complete learning experience with 
            <span className="text-cyan-400"> AI-powered </span> summaries, quizzes, and notes.
          </p>

          {/* Feature Pills */}
          <div className="flex flex-wrap justify-center gap-3 mb-10 animate-fade-in-up" style={{ animationDelay: '0.3s' }}>
            {features.map((f, i) => (
              <div 
                key={f.label}
                className={`flex items-center gap-2 px-4 py-2 rounded-full bg-gradient-to-r ${f.color} bg-opacity-10 border border-white/10`}
                style={{ animationDelay: `${i * 0.1}s` }}
              >
                <f.icon className="text-white text-sm" />
                <span className="text-white text-sm font-medium">{f.label}</span>
              </div>
            ))}
          </div>
          
          {/* Search Bar */}
          <div className="animate-fade-in-up" style={{ animationDelay: '0.4s' }}>
            <SearchBar query={query} setQuery={setQuery} onSearch={handleSearch} loading={loading} />
          </div>

          {/* Hint */}
          {!searched && (
            <p className="mt-6 text-sm text-gray-500 flex items-center justify-center gap-2 animate-fade-in" style={{ animationDelay: '0.6s' }}>
              <HiSparkles className="text-cyan-400" />
              Try searching "Python tutorial", "Machine Learning basics", or "Web development"
            </p>
          )}
        </div>

        {/* Loading State */}
        {loading && (
          <div className="animate-fade-in">
            <LoadingSpinner text="Searching YouTube..." />
          </div>
        )}

        {/* Results Grid */}
        {!loading && videos.length > 0 && (
          <div className="animate-fade-in-up">
            <div className="flex items-center gap-3 mb-6">
              <div className="flex items-center gap-2 px-4 py-2 bg-red-500/10 rounded-full border border-red-500/30">
                <FaYoutube className="text-red-500" />
                <span className="text-sm text-white font-medium">Results</span>
              </div>
              <h2 className="text-lg text-gray-400">
                for "<span className="text-cyan-400 font-medium">{query}</span>"
              </h2>
              <span className="text-xs text-gray-600 bg-dark/50 px-2 py-1 rounded-full">{videos.length} videos</span>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {videos.map((v, index) => (
                <div 
                  key={v.video_id} 
                  className="animate-fade-in-up"
                  style={{ animationDelay: `${index * 0.1}s` }}
                >
                  <VideoCard video={v} />
                </div>
              ))}
            </div>
          </div>
        )}

        {/* No Results */}
        {!loading && searched && videos.length === 0 && (
          <div className="text-center py-12 animate-fade-in">
            <FaRocket className="text-4xl text-gray-600 mx-auto mb-4" />
            <p className="text-gray-500">No results found. Try a different search term.</p>
          </div>
        )}
      </div>
    </div>
  )
}
