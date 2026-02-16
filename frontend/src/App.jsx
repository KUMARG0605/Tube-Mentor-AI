import { Routes, Route } from 'react-router-dom'
import Navbar from './components/Navbar'
import HomePage from './pages/HomePage'
import VideoPage from './pages/VideoPage'
import AboutPage from './pages/AboutPage'

// Root application component - layout wrapper with routing
function App() {
  return (
    <div className="min-h-screen bg-[#0a0a1a]">
      <Navbar />
      <main>
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/video/:videoId" element={<VideoPage />} />
          <Route path="/about" element={<AboutPage />} />
        </Routes>
      </main>
    </div>
  )
}

export default App
