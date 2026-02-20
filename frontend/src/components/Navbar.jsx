import { useState, useEffect } from 'react'
import { Link, useLocation } from 'react-router-dom'
import { FaBrain, FaBars, FaTimes, FaHome, FaNewspaper, FaEnvelope, FaRoad, FaUser, FaSignOutAlt, FaChevronDown } from 'react-icons/fa'
import { HiSparkles } from 'react-icons/hi'
import { useAuth } from '../context/AuthContext'

export default function Navbar() {
  const [isMenuOpen, setIsMenuOpen] = useState(false)
  const [showUserMenu, setShowUserMenu] = useState(false)
  const [phases, setPhases] = useState({ phase1_core: true, phase2_intelligence: false, phase3_content: false, phase4_publishing: false })
  const location = useLocation()
  const { user, logout, isAuthenticated } = useAuth()

  useEffect(() => {
    fetch('http://localhost:8000/')
      .then(res => res.json())
      .then(data => {
        if (data.phases) setPhases(data.phases)
      })
      .catch(() => {})
  }, [])

  useEffect(() => {
    setIsMenuOpen(false)
    setShowUserMenu(false)
  }, [location])

  const navLinks = [
    { to: '/', label: 'Home', icon: <FaHome /> },
    { to: '/blogs', label: 'Blogs', icon: <FaNewspaper /> },
    { to: '/journey', label: 'My Journey', icon: <FaRoad /> },
    { to: '/contact', label: 'Contact', icon: <FaEnvelope /> },
  ]

  const getModeBadge = () => {
    if (phases.phase4_publishing) return { label: 'Creator Pro', color: 'from-emerald-400 to-cyan-400', icon: '🚀' }
    if (phases.phase3_content) return { label: 'Create Mode', color: 'from-purple-400 to-pink-400', icon: '✨' }
    if (phases.phase2_intelligence) return { label: 'Smart Mode', color: 'from-cyan-400 to-blue-400', icon: '🧠' }
    return { label: 'Learn Mode', color: 'from-cyan-500 to-purple-500', icon: '📚' }
  }

  const modeBadge = getModeBadge()

  return (
    <nav className="bg-secondary/90 backdrop-blur-xl border-b border-cyan-500/20 sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4">
        <div className="flex items-center justify-between h-16">
          {/* Logo */}
          <Link to="/" className="flex items-center gap-2 group">
            <div className="relative">
              <FaBrain className="text-cyan-400 text-2xl group-hover:scale-110 transition-transform duration-300" />
              <div className="absolute -inset-1 bg-cyan-400/20 rounded-full blur-md group-hover:blur-lg transition-all opacity-0 group-hover:opacity-100" />
            </div>
            <span className="text-xl font-bold">
              <span className="bg-gradient-to-r from-cyan-400 to-purple-400 bg-clip-text text-transparent">Tube</span>
              <span className="text-white">Mentor</span>
              <span className="text-cyan-400/60 ml-1 text-sm font-normal">AI</span>
            </span>
          </Link>

          {/* Desktop Navigation */}
          <div className="hidden md:flex items-center gap-1">
            {navLinks.map((link, index) => (
              <Link
                key={link.to}
                to={link.to}
                className={`flex items-center gap-2 px-4 py-2 rounded-xl text-sm font-medium transition-all duration-300
                  hover:scale-105 active:scale-95
                  ${location.pathname === link.to 
                    ? 'bg-gradient-to-r from-cyan-500/20 to-purple-500/20 text-cyan-400 shadow-lg shadow-cyan-500/10' 
                    : 'text-gray-400 hover:text-white hover:bg-white/5'}`}
                style={{ animationDelay: `${index * 100}ms` }}
              >
                <span className={location.pathname === link.to ? 'animate-bounce-in' : ''}>{link.icon}</span>
                {link.label}
              </Link>
            ))}
          </div>

          {/* Right side: Mode Badge + Auth */}
          <div className="flex items-center gap-3">
            {/* Mode Badge */}
            <div className={`hidden sm:flex items-center gap-2 px-3 py-1.5 rounded-full 
                          bg-gradient-to-r ${modeBadge.color} bg-opacity-10 
                          border border-white/10 animate-pulse-glow`}>
              <span className="text-sm">{modeBadge.icon}</span>
              <span className="text-xs font-medium text-white">{modeBadge.label}</span>
              <HiSparkles className="text-yellow-300 text-xs animate-pulse" />
            </div>

            {/* User Profile or Login Button */}
            {isAuthenticated ? (
              <div className="relative">
                <button
                  onClick={() => setShowUserMenu(!showUserMenu)}
                  className="flex items-center gap-2 px-3 py-2 rounded-xl text-sm
                           bg-dark/50 border border-cyan-500/30 hover:border-cyan-500/50
                           transition-all duration-300 group"
                >
                  {user?.avatar_url ? (
                    <img 
                      src={user.avatar_url} 
                      alt={user.full_name || 'User'} 
                      className="w-7 h-7 rounded-full ring-2 ring-cyan-500/50"
                    />
                  ) : (
                    <div className="w-7 h-7 rounded-full bg-gradient-to-br from-cyan-500 to-purple-500 flex items-center justify-center">
                      <span className="text-xs text-white font-medium">
                        {(user?.full_name || user?.email || 'U')[0].toUpperCase()}
                      </span>
                    </div>
                  )}
                  <span className="hidden sm:inline text-white max-w-[100px] truncate">
                    {user?.full_name || user?.email?.split('@')[0]}
                  </span>
                  <FaChevronDown className={`text-gray-400 text-xs transition-transform ${showUserMenu ? 'rotate-180' : ''}`} />
                </button>

                {/* Dropdown Menu */}
                {showUserMenu && (
                  <div className="absolute right-0 top-full mt-2 w-48 bg-secondary border border-cyan-500/20 rounded-xl shadow-xl animate-fade-in-down overflow-hidden">
                    <div className="p-3 border-b border-cyan-500/10">
                      <p className="text-sm font-medium text-white truncate">{user?.full_name || 'User'}</p>
                      <p className="text-xs text-gray-400 truncate">{user?.email}</p>
                    </div>
                    <button
                      onClick={() => { logout(); setShowUserMenu(false); }}
                      className="w-full flex items-center gap-2 px-4 py-3 text-sm text-gray-400 hover:bg-dark/50 hover:text-red-400 transition-colors"
                    >
                      <FaSignOutAlt />
                      Sign Out
                    </button>
                  </div>
                )}
              </div>
            ) : (
              <Link
                to="/login"
                className="flex items-center gap-2 px-4 py-2 rounded-xl text-sm font-medium
                         bg-gradient-to-r from-cyan-500 to-purple-500 text-white
                         hover:from-cyan-400 hover:to-purple-400 hover:scale-105 
                         active:scale-95 transition-all duration-300 shadow-lg shadow-cyan-500/25"
              >
                <FaUser className="text-xs" />
                <span className="hidden sm:inline">Login</span>
              </Link>
            )}

            {/* Mobile Menu Button */}
            <button
              onClick={() => setIsMenuOpen(!isMenuOpen)}
              className="md:hidden p-2 text-gray-400 hover:text-cyan-400 transition-colors rounded-lg hover:bg-white/5"
              aria-label="Toggle menu"
            >
              {isMenuOpen ? <FaTimes size={20} className="animate-scale-in" /> : <FaBars size={20} />}
            </button>
          </div>
        </div>

        {/* Mobile Menu */}
        {isMenuOpen && (
          <div className="md:hidden border-t border-cyan-500/20 py-4 space-y-1 animate-fade-in-down">
            {navLinks.map((link, index) => (
              <Link
                key={link.to}
                to={link.to}
                className={`flex items-center gap-3 px-4 py-3 rounded-xl transition-all duration-300
                  animate-slide-in-left
                  ${location.pathname === link.to 
                    ? 'bg-gradient-to-r from-cyan-500/20 to-purple-500/20 text-cyan-400' 
                    : 'text-gray-400 hover:bg-dark/50 hover:text-white'}`}
                style={{ animationDelay: `${index * 50}ms` }}
              >
                {link.icon}
                {link.label}
              </Link>
            ))}
            
            {/* Mobile Mode Badge */}
            <div className="px-4 pt-4 border-t border-cyan-500/10 mt-4">
              <div className={`inline-flex items-center gap-2 px-3 py-1.5 rounded-full 
                            bg-gradient-to-r ${modeBadge.color} bg-opacity-20`}>
                <span>{modeBadge.icon}</span>
                <span className="text-xs text-white font-medium">{modeBadge.label}</span>
              </div>
            </div>

            {/* Mobile Auth */}
            <div className="px-4 pt-2">
              {isAuthenticated ? (
                <div className="space-y-2">
                  <div className="flex items-center gap-3 p-3 bg-dark/50 rounded-xl">
                    {user?.avatar_url ? (
                      <img src={user.avatar_url} alt="" className="w-10 h-10 rounded-full" />
                    ) : (
                      <div className="w-10 h-10 rounded-full bg-gradient-to-br from-cyan-500 to-purple-500 flex items-center justify-center">
                        <span className="text-white font-medium">{(user?.full_name || 'U')[0]}</span>
                      </div>
                    )}
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-medium text-white truncate">{user?.full_name || 'User'}</p>
                      <p className="text-xs text-gray-400 truncate">{user?.email}</p>
                    </div>
                  </div>
                  <button
                    onClick={logout}
                    className="flex items-center justify-center gap-2 w-full px-4 py-3 rounded-xl
                             bg-red-500/10 border border-red-500/30 text-red-400 
                             hover:bg-red-500/20 transition-all"
                  >
                    <FaSignOutAlt />
                    Sign Out
                  </button>
                </div>
              ) : (
                <Link
                  to="/login"
                  className="flex items-center justify-center gap-2 w-full px-4 py-3 rounded-xl
                           bg-gradient-to-r from-cyan-500 to-purple-500 text-white font-medium
                           hover:from-cyan-400 hover:to-purple-400 transition-all"
                >
                  <FaUser />
                  Login / Sign Up
                </Link>
              )}
            </div>
          </div>
        )}
      </div>
    </nav>
  )
}
