import { Routes, Route } from 'react-router-dom'
import { AuthProvider } from './context/AuthContext'
import Navbar from './components/Navbar'
import HomePage from './pages/HomePage'
import VideoPage from './pages/VideoPage'
import AboutPage from './pages/AboutPage'
import BlogsPage from './pages/BlogsPage'
import JourneyPage from './pages/JourneyPage'
import ContactPage from './pages/ContactPage'
import LoginPage from './pages/LoginPage'
import AuthCallback from './pages/AuthCallback'

function App() {
  return (
    <AuthProvider>
      <div className="min-h-screen bg-[#020617]">
        <Navbar />
        <main>
          <Routes>
            <Route path="/" element={<HomePage />} />
            <Route path="/video/:videoId" element={<VideoPage />} />
            <Route path="/about" element={<AboutPage />} />
            <Route path="/blogs" element={<BlogsPage />} />
            <Route path="/journey" element={<JourneyPage />} />
            <Route path="/contact" element={<ContactPage />} />
            <Route path="/login" element={<LoginPage />} />
            <Route path="/auth/callback" element={<AuthCallback />} />
          </Routes>
        </main>
      </div>
    </AuthProvider>
  )
}

export default App
