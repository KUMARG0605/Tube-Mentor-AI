import { Routes, Route } from 'react-router-dom'
import Navbar from './components/Navbar'
import HomePage from './pages/HomePage'
import VideoPage from './pages/VideoPage'

// Root application component - layout wrapper with routing
function App() {
  return (
    <div className="min-h-screen bg-[#0a0a1a]">
      <Navbar />
      <main className="max-w-7xl mx-auto px-4 py-6">
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/video/:videoId" element={<VideoPage />} />
        </Routes>
      </main>
    </div>
  )
}

export default App
