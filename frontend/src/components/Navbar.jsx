import { useState, useEffect } from 'react'
import { Link, useLocation } from 'react-router-dom'
import { FaBrain, FaBars, FaTimes, FaHome, FaInfoCircle, FaGithub, FaRocket } from 'react-icons/fa'

export default function Navbar() {
  const [isMenuOpen, setIsMenuOpen] = useState(false)
  const [phases, setPhases] = useState({ phase1_core: true, phase2_intelligence: false })
  const location = useLocation()

  // Fetch phase status from API
  useEffect(() => {
    fetch('http://localhost:8000/')
      .then(res => res.json())
      .then(data => {
        if (data.phases) setPhases(data.phases)
      })
      .catch(() => {})
  }, [])

  // Close menu on route change
  useEffect(() => {
    setIsMenuOpen(false)
  }, [location])

  const navLinks = [
    { to: '/', label: 'Home', icon: <FaHome /> },
    { to: '/about', label: 'About', icon: <FaInfoCircle /> },
  ]

  const activePhases = Object.entries(phases).filter(([_, v]) => v).length
  const totalPhases = 4

  return (
    <nav className="bg-secondary/95 backdrop-blur-md border-b border-primary/20 sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4">
        <div className="flex items-center justify-between h-16">
          {/* Logo */}
          <Link to="/" className="flex items-center gap-2 group">
            <FaBrain className="text-primary text-2xl group-hover:rotate-12 transition-transform" />
            <span className="text-xl font-bold">
              <span className="text-primary">Tube</span>
              <span className="text-white">Mentor</span>
              <span className="text-primary/60 ml-1 text-sm font-normal">AI</span>
            </span>
          </Link>

          {/* Desktop Navigation */}
          <div className="hidden md:flex items-center gap-6">
            {navLinks.map(link => (
              <Link
                key={link.to}
                to={link.to}
                className={`flex items-center gap-2 text-sm font-medium transition-colors
                  ${location.pathname === link.to 
                    ? 'text-primary' 
                    : 'text-gray-400 hover:text-white'}`}
              >
                {link.icon}
                {link.label}
              </Link>
            ))}
            <a
              href="https://github.com"
              target="_blank"
              rel="noopener noreferrer"
              className="flex items-center gap-2 text-sm text-gray-400 hover:text-white transition-colors"
            >
              <FaGithub />
              GitHub
            </a>
          </div>

          {/* Phase Indicator + Mobile Menu Button */}
          <div className="flex items-center gap-4">
            {/* Phase Badge */}
            <div className="hidden sm:flex items-center gap-2 bg-dark/50 px-3 py-1.5 rounded-full border border-primary/30">
              <FaRocket className="text-primary text-xs" />
              <span className="text-xs text-gray-400">
                Phase <span className="text-primary font-semibold">{activePhases}</span>/{totalPhases}
              </span>
              {phases.phase2_intelligence && (
                <span className="text-[10px] bg-primary/20 text-primary px-1.5 py-0.5 rounded">
                  AI+
                </span>
              )}
            </div>

            {/* Mobile Menu Button */}
            <button
              onClick={() => setIsMenuOpen(!isMenuOpen)}
              className="md:hidden p-2 text-gray-400 hover:text-white transition-colors"
              aria-label="Toggle menu"
            >
              {isMenuOpen ? <FaTimes size={20} /> : <FaBars size={20} />}
            </button>
          </div>
        </div>

        {/* Mobile Menu */}
        {isMenuOpen && (
          <div className="md:hidden border-t border-primary/20 py-4 space-y-2">
            {navLinks.map(link => (
              <Link
                key={link.to}
                to={link.to}
                className={`flex items-center gap-3 px-4 py-3 rounded-lg transition-colors
                  ${location.pathname === link.to 
                    ? 'bg-primary/10 text-primary' 
                    : 'text-gray-400 hover:bg-dark/50 hover:text-white'}`}
              >
                {link.icon}
                {link.label}
              </Link>
            ))}
            <a
              href="https://github.com"
              target="_blank"
              rel="noopener noreferrer"
              className="flex items-center gap-3 px-4 py-3 rounded-lg text-gray-400 hover:bg-dark/50 hover:text-white transition-colors"
            >
              <FaGithub />
              GitHub
            </a>
            
            {/* Mobile Phase Info */}
            <div className="px-4 pt-4 border-t border-primary/10 mt-4">
              <div className="flex items-center gap-2 text-xs text-gray-500">
                <FaRocket className="text-primary" />
                <span>
                  Phase {activePhases} of {totalPhases} active
                  {phases.phase2_intelligence && ' • AI Recommendations enabled'}
                </span>
              </div>
            </div>
          </div>
        )}
      </div>
    </nav>
  )
}
