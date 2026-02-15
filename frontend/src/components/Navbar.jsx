import { Link } from 'react-router-dom'
import { FaBrain } from 'react-icons/fa'

export default function Navbar() {
  return (
    <nav className="bg-secondary/80 backdrop-blur-md border-b border-primary/20 sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 py-3 flex items-center justify-between">
        <Link to="/" className="flex items-center gap-2 group">
          <FaBrain className="text-primary text-2xl group-hover:rotate-12 transition-transform" />
          <span className="text-xl font-bold">
            <span className="text-primary">Tube</span>
            <span className="text-white">Mentor</span>
            <span className="text-primary/60 ml-1 text-sm font-normal">AI</span>
          </span>
        </Link>
        <div className="text-xs text-gray-500">Phase 1 — Core Agent</div>
      </div>
    </nav>
  )
}
