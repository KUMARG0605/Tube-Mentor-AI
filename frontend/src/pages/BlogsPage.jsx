import { useState } from 'react'
import { 
  FaNewspaper, FaPen, FaClock, FaUser, FaHeart, FaComment,
  FaTags, FaSearch, FaFire, FaStar, FaTimes, FaImage
} from 'react-icons/fa'

// Sample blog data (will be replaced with API data)
const sampleBlogs = [
  {
    id: 1,
    title: "Getting Started with AI-Powered Learning",
    excerpt: "Discover how AI is transforming the way we learn from YouTube videos. From automatic transcripts to smart summaries...",
    author: "Admin/Kumar",
    date: "Feb 18, 2026",
    readTime: "5 min",
    likes: 42,
    comments: 8,
    tags: ["AI", "Learning", "Education"],
    featured: true,
    image: "https://images.unsplash.com/photo-1677442136019-21780ecad995?w=600"
  },
  {
    id: 2,
    title: "How to Maximize Your Study Sessions",
    excerpt: "Tips and tricks to get the most out of TubeMentor AI. Learn how to use quizzes effectively and create perfect study notes...",
    author: "Admin",
    date: "Feb 15, 2026",
    readTime: "4 min",
    likes: 35,
    comments: 12,
    tags: ["Study Tips", "Productivity"],
    featured: false,
    image: "https://images.unsplash.com/photo-1434030216411-0b793f4b4173?w=600"
  },
  {
    id: 3,
    title: "The Future of Video-Based Education",
    excerpt: "Exploring trends in video learning and how AI assistants are making education more accessible to everyone...",
    author: "Admin",
    date: "Feb 10, 2026",
    readTime: "6 min",
    likes: 58,
    comments: 15,
    tags: ["Future", "EdTech", "Trends"],
    featured: false,
    image: "https://images.unsplash.com/photo-1516321318423-f06f85e504b3?w=600"
  }
]

export default function BlogsPage() {
  const [blogs] = useState(sampleBlogs)
  const [searchQuery, setSearchQuery] = useState('')
  const [selectedTag, setSelectedTag] = useState(null)
  const [showWriteModal, setShowWriteModal] = useState(false)
  const [newBlog, setNewBlog] = useState({ title: '', content: '', tags: '' })

  const allTags = [...new Set(blogs.flatMap(b => b.tags))]
  
  const filteredBlogs = blogs.filter(blog => {
    const matchesSearch = blog.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
                         blog.excerpt.toLowerCase().includes(searchQuery.toLowerCase())
    const matchesTag = !selectedTag || blog.tags.includes(selectedTag)
    return matchesSearch && matchesTag
  })

  const featuredBlog = blogs.find(b => b.featured)

  return (
    <div className="min-h-screen py-12 px-4">
      {/* Hero Section */}
      <div className="max-w-6xl mx-auto mb-12">
        <div className="text-center mb-8">
          <div className="inline-flex items-center gap-2 bg-primary/10 px-4 py-2 rounded-full mb-6">
            <FaNewspaper className="text-primary" />
            <span className="text-sm text-gray-400">Knowledge Share Hub</span>
          </div>
          
          <h1 className="text-4xl md:text-5xl font-bold mb-4">
            <span className="bg-gradient-to-r from-primary via-purple-500 to-pink-500 bg-clip-text text-transparent">
              Blog & Insights
            </span>
          </h1>
          <p className="text-gray-400 max-w-2xl mx-auto">
            Discover tips, tutorials, and insights about AI-powered learning, 
            productivity hacks, and the future of education.
          </p>
        </div>

        {/* Search & Actions */}
        <div className="flex flex-col sm:flex-row gap-4 items-center justify-between">
          <div className="relative flex-1 max-w-md w-full">
            <FaSearch className="absolute left-4 top-1/2 -translate-y-1/2 text-gray-500" />
            <input
              type="text"
              placeholder="Search articles..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full bg-secondary border border-gray-700 rounded-xl pl-11 pr-4 py-3
                       text-white placeholder-gray-500 focus:border-primary outline-none transition-all"
            />
          </div>
          
          <button
            onClick={() => setShowWriteModal(true)}
            className="flex items-center gap-2 px-6 py-3 bg-gradient-to-r from-primary to-purple-500
                     text-white font-semibold rounded-xl hover:opacity-90 transition-all group"
          >
            <FaPen className="group-hover:rotate-12 transition-transform" />
            Write a Post
          </button>
        </div>

        {/* Tags */}
        <div className="flex flex-wrap gap-2 mt-6 justify-center">
          <button
            onClick={() => setSelectedTag(null)}
            className={`px-4 py-2 rounded-full text-sm transition-all
              ${!selectedTag 
                ? 'bg-primary text-white' 
                : 'bg-secondary text-gray-400 hover:text-white'}`}
          >
            All Posts
          </button>
          {allTags.map(tag => (
            <button
              key={tag}
              onClick={() => setSelectedTag(tag)}
              className={`px-4 py-2 rounded-full text-sm transition-all
                ${selectedTag === tag 
                  ? 'bg-primary text-white' 
                  : 'bg-secondary text-gray-400 hover:text-white'}`}
            >
              {tag}
            </button>
          ))}
        </div>
      </div>

      {/* Featured Post */}
      {featuredBlog && !searchQuery && !selectedTag && (
        <div className="max-w-6xl mx-auto mb-12">
          <div className="group bg-gradient-to-br from-secondary to-dark rounded-2xl overflow-hidden border border-primary/20 hover:border-primary/40 transition-all">
            <div className="grid md:grid-cols-2">
              <div className="relative h-64 md:h-auto overflow-hidden">
                <img 
                  src={featuredBlog.image} 
                  alt={featuredBlog.title}
                  className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500"
                />
                <div className="absolute top-4 left-4 flex items-center gap-2 bg-gradient-to-r from-yellow-500 to-orange-500 px-3 py-1 rounded-full">
                  <FaStar className="text-white text-xs" />
                  <span className="text-white text-xs font-semibold">Featured</span>
                </div>
              </div>
              <div className="p-8 flex flex-col justify-center">
                <div className="flex flex-wrap gap-2 mb-4">
                  {featuredBlog.tags.map(tag => (
                    <span key={tag} className="text-xs bg-primary/20 text-primary px-2 py-1 rounded">
                      {tag}
                    </span>
                  ))}
                </div>
                <h2 className="text-2xl font-bold text-white mb-3 group-hover:text-primary transition-colors">
                  {featuredBlog.title}
                </h2>
                <p className="text-gray-400 mb-6">{featuredBlog.excerpt}</p>
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-4 text-sm text-gray-500">
                    <span className="flex items-center gap-1">
                      <FaUser className="text-primary" />
                      {featuredBlog.author}
                    </span>
                    <span className="flex items-center gap-1">
                      <FaClock />
                      {featuredBlog.readTime}
                    </span>
                  </div>
                  <div className="flex items-center gap-4 text-sm text-gray-500">
                    <span className="flex items-center gap-1">
                      <FaHeart className="text-pink-500" />
                      {featuredBlog.likes}
                    </span>
                    <span className="flex items-center gap-1">
                      <FaComment className="text-primary" />
                      {featuredBlog.comments}
                    </span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Blog Grid */}
      <div className="max-w-6xl mx-auto">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-xl font-semibold text-white flex items-center gap-2">
            <FaFire className="text-orange-500" />
            {selectedTag ? `Posts tagged "${selectedTag}"` : 'Latest Posts'}
          </h2>
          <span className="text-sm text-gray-500">{filteredBlogs.length} articles</span>
        </div>

        {filteredBlogs.length > 0 ? (
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            {filteredBlogs.filter(b => !b.featured || searchQuery || selectedTag).map(blog => (
              <article 
                key={blog.id}
                className="group bg-gradient-to-br from-secondary to-dark rounded-xl overflow-hidden
                         border border-gray-800 hover:border-primary/30 transition-all cursor-pointer"
              >
                <div className="relative h-48 overflow-hidden">
                  <img 
                    src={blog.image} 
                    alt={blog.title}
                    className="w-full h-full object-cover group-hover:scale-110 transition-transform duration-500"
                  />
                  <div className="absolute inset-0 bg-gradient-to-t from-dark/80 to-transparent" />
                  <div className="absolute bottom-3 left-3 flex gap-2">
                    {blog.tags.slice(0, 2).map(tag => (
                      <span key={tag} className="text-xs bg-primary/80 text-white px-2 py-0.5 rounded">
                        {tag}
                      </span>
                    ))}
                  </div>
                </div>
                <div className="p-5">
                  <h3 className="text-lg font-semibold text-white mb-2 group-hover:text-primary transition-colors line-clamp-2">
                    {blog.title}
                  </h3>
                  <p className="text-gray-400 text-sm mb-4 line-clamp-2">{blog.excerpt}</p>
                  <div className="flex items-center justify-between text-xs text-gray-500">
                    <div className="flex items-center gap-3">
                      <span className="flex items-center gap-1">
                        <FaUser className="text-primary" />
                        {blog.author}
                      </span>
                      <span>{blog.date}</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <span className="flex items-center gap-1">
                        <FaHeart className="text-pink-500" /> {blog.likes}
                      </span>
                    </div>
                  </div>
                </div>
              </article>
            ))}
          </div>
        ) : (
          <div className="text-center py-12">
            <FaSearch className="text-4xl text-gray-600 mx-auto mb-4" />
            <p className="text-gray-400">No posts found matching your criteria</p>
          </div>
        )}
      </div>

      {/* Write Blog Modal */}
      {showWriteModal && (
        <div className="fixed inset-0 bg-black/70 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-secondary rounded-2xl w-full max-w-2xl max-h-[90vh] overflow-y-auto">
            <div className="p-6 border-b border-gray-700 flex items-center justify-between">
              <h2 className="text-xl font-semibold text-white flex items-center gap-2">
                <FaPen className="text-primary" />
                Write a New Post
              </h2>
              <button 
                onClick={() => setShowWriteModal(false)}
                className="p-2 text-gray-400 hover:text-white transition-colors"
              >
                <FaTimes />
              </button>
            </div>
            
            <form className="p-6 space-y-5">
              <div>
                <label className="block text-sm text-gray-400 mb-2">Title</label>
                <input
                  type="text"
                  value={newBlog.title}
                  onChange={(e) => setNewBlog({...newBlog, title: e.target.value})}
                  className="w-full bg-dark border border-gray-700 rounded-xl px-4 py-3 text-white
                           focus:border-primary outline-none transition-all"
                  placeholder="Enter a catchy title..."
                />
              </div>

              <div>
                <label className="block text-sm text-gray-400 mb-2">Cover Image URL</label>
                <div className="flex gap-2">
                  <input
                    type="url"
                    className="flex-1 bg-dark border border-gray-700 rounded-xl px-4 py-3 text-white
                             focus:border-primary outline-none transition-all"
                    placeholder="https://example.com/image.jpg"
                  />
                  <button type="button" className="px-4 py-3 bg-dark border border-gray-700 rounded-xl text-gray-400 hover:text-white">
                    <FaImage />
                  </button>
                </div>
              </div>

              <div>
                <label className="block text-sm text-gray-400 mb-2">Content</label>
                <textarea
                  value={newBlog.content}
                  onChange={(e) => setNewBlog({...newBlog, content: e.target.value})}
                  rows={8}
                  className="w-full bg-dark border border-gray-700 rounded-xl px-4 py-3 text-white
                           focus:border-primary outline-none transition-all resize-none"
                  placeholder="Write your article content here... (Markdown supported)"
                />
              </div>

              <div>
                <label className="block text-sm text-gray-400 mb-2">
                  <FaTags className="inline mr-2" />
                  Tags (comma-separated)
                </label>
                <input
                  type="text"
                  value={newBlog.tags}
                  onChange={(e) => setNewBlog({...newBlog, tags: e.target.value})}
                  className="w-full bg-dark border border-gray-700 rounded-xl px-4 py-3 text-white
                           focus:border-primary outline-none transition-all"
                  placeholder="AI, Learning, Tutorial"
                />
              </div>

              <div className="flex gap-3 pt-4">
                <button
                  type="button"
                  onClick={() => setShowWriteModal(false)}
                  className="flex-1 py-3 bg-dark text-gray-400 rounded-xl hover:text-white transition-colors"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="flex-1 py-3 bg-gradient-to-r from-primary to-purple-500 text-white font-semibold
                           rounded-xl hover:opacity-90 transition-all"
                >
                  Publish Post
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Decorative elements */}
      <div className="fixed top-40 right-10 w-72 h-72 bg-purple-500/5 rounded-full blur-3xl pointer-events-none" />
      <div className="fixed bottom-20 left-10 w-80 h-80 bg-primary/5 rounded-full blur-3xl pointer-events-none" />
    </div>
  )
}
