import { useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import { 
  FaEnvelope, FaLock, FaUser, FaGoogle, FaEye, FaEyeSlash,
  FaBrain, FaArrowRight, FaSpinner, FaCheck
} from 'react-icons/fa'
import { HiSparkles } from 'react-icons/hi'

export default function LoginPage() {
  const [isLogin, setIsLogin] = useState(true)
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [fullName, setFullName] = useState('')
  const [showPassword, setShowPassword] = useState(false)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')
  
  const { login, signup, loginWithGoogle } = useAuth()
  const navigate = useNavigate()

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    setLoading(true)

    try {
      if (isLogin) {
        await login(email, password)
      } else {
        await signup(email, password, fullName)
      }
      setSuccess('Success! Redirecting...')
      setTimeout(() => navigate('/'), 1500)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  const handleGoogleLogin = () => {
    // Initialize Google OAuth
    const clientId = import.meta.env.VITE_GOOGLE_CLIENT_ID
    if (!clientId) {
      setError('Google OAuth not configured')
      return
    }
    
    const redirectUri = window.location.origin + '/auth/callback'
    const scope = 'email profile'
    const responseType = 'token'
    
    const googleAuthUrl = `https://accounts.google.com/o/oauth2/v2/auth?client_id=${clientId}&redirect_uri=${redirectUri}&scope=${scope}&response_type=${responseType}`
    
    window.location.href = googleAuthUrl
  }

  return (
    <div className="min-h-screen flex items-center justify-center px-4 py-12 relative overflow-hidden">
      {/* Animated background elements */}
      <div className="absolute inset-0 overflow-hidden">
        <div className="absolute top-1/4 -left-20 w-96 h-96 bg-cyan-500/10 rounded-full blur-3xl animate-float" />
        <div className="absolute bottom-1/4 -right-20 w-96 h-96 bg-purple-500/10 rounded-full blur-3xl animate-float" style={{ animationDelay: '1.5s' }} />
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[600px] bg-gradient-radial from-cyan-500/5 to-transparent rounded-full" />
      </div>

      <div className="w-full max-w-md relative animate-fade-in-up">
        {/* Logo Header */}
        <div className="text-center mb-8 animate-fade-in-down">
          <Link to="/" className="inline-flex items-center gap-3 group">
            <div className="relative">
              <FaBrain className="text-4xl text-cyan-400 group-hover:scale-110 transition-transform" />
              <div className="absolute -inset-2 bg-cyan-400/20 rounded-full blur-lg opacity-0 group-hover:opacity-100 transition-opacity" />
            </div>
            <span className="text-2xl font-bold">
              <span className="bg-gradient-to-r from-cyan-400 to-purple-400 bg-clip-text text-transparent">Tube</span>
              <span className="text-white">Mentor</span>
            </span>
          </Link>
          <p className="mt-4 text-gray-400">
            {isLogin ? 'Welcome back! Sign in to continue learning.' : 'Join us and start your learning journey.'}
          </p>
        </div>

        {/* Main Card */}
        <div className="bg-secondary/80 backdrop-blur-xl rounded-2xl border border-cyan-500/20 p-8 shadow-xl shadow-cyan-500/5 animate-scale-in">
          {/* Toggle Tabs */}
          <div className="flex mb-8 bg-dark/50 rounded-xl p-1">
            <button
              onClick={() => { setIsLogin(true); setError(''); }}
              className={`flex-1 py-3 rounded-lg font-medium transition-all duration-300 ${
                isLogin 
                  ? 'bg-gradient-to-r from-cyan-500 to-purple-500 text-white shadow-lg' 
                  : 'text-gray-400 hover:text-white'
              }`}
            >
              Sign In
            </button>
            <button
              onClick={() => { setIsLogin(false); setError(''); }}
              className={`flex-1 py-3 rounded-lg font-medium transition-all duration-300 ${
                !isLogin 
                  ? 'bg-gradient-to-r from-cyan-500 to-purple-500 text-white shadow-lg' 
                  : 'text-gray-400 hover:text-white'
              }`}
            >
              Sign Up
            </button>
          </div>

          {/* Error/Success Messages */}
          {error && (
            <div className="mb-6 p-4 bg-red-500/10 border border-red-500/30 rounded-xl text-red-400 text-sm animate-fade-in">
              {error}
            </div>
          )}
          {success && (
            <div className="mb-6 p-4 bg-green-500/10 border border-green-500/30 rounded-xl text-green-400 text-sm flex items-center gap-2 animate-fade-in">
              <FaCheck className="animate-bounce-in" />
              {success}
            </div>
          )}

          {/* Form */}
          <form onSubmit={handleSubmit} className="space-y-5">
            {/* Full Name (Signup only) */}
            {!isLogin && (
              <div className="animate-fade-in-down">
                <label className="block text-sm text-gray-400 mb-2">Full Name</label>
                <div className="relative group">
                  <FaUser className="absolute left-4 top-1/2 -translate-y-1/2 text-gray-500 group-focus-within:text-cyan-400 transition-colors" />
                  <input
                    type="text"
                    value={fullName}
                    onChange={(e) => setFullName(e.target.value)}
                    className="w-full bg-dark/50 border border-gray-700 rounded-xl pl-12 pr-4 py-3.5 text-white
                             placeholder-gray-500 focus:border-cyan-500 focus:ring-2 focus:ring-cyan-500/20 
                             outline-none transition-all duration-300"
                    placeholder="John Doe"
                  />
                </div>
              </div>
            )}

            {/* Email */}
            <div>
              <label className="block text-sm text-gray-400 mb-2">Email Address</label>
              <div className="relative group">
                <FaEnvelope className="absolute left-4 top-1/2 -translate-y-1/2 text-gray-500 group-focus-within:text-cyan-400 transition-colors" />
                <input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className="w-full bg-dark/50 border border-gray-700 rounded-xl pl-12 pr-4 py-3.5 text-white
                           placeholder-gray-500 focus:border-cyan-500 focus:ring-2 focus:ring-cyan-500/20 
                           outline-none transition-all duration-300"
                  placeholder="you@example.com"
                  required
                />
              </div>
            </div>

            {/* Password */}
            <div>
              <label className="block text-sm text-gray-400 mb-2">Password</label>
              <div className="relative group">
                <FaLock className="absolute left-4 top-1/2 -translate-y-1/2 text-gray-500 group-focus-within:text-cyan-400 transition-colors" />
                <input
                  type={showPassword ? 'text' : 'password'}
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="w-full bg-dark/50 border border-gray-700 rounded-xl pl-12 pr-12 py-3.5 text-white
                           placeholder-gray-500 focus:border-cyan-500 focus:ring-2 focus:ring-cyan-500/20 
                           outline-none transition-all duration-300"
                  placeholder="••••••••"
                  required
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-4 top-1/2 -translate-y-1/2 text-gray-500 hover:text-cyan-400 transition-colors"
                >
                  {showPassword ? <FaEyeSlash /> : <FaEye />}
                </button>
              </div>
            </div>

            {/* Forgot Password (Login only) */}
            {isLogin && (
              <div className="text-right">
                <a href="#" className="text-sm text-cyan-400 hover:text-cyan-300 transition-colors">
                  Forgot password?
                </a>
              </div>
            )}

            {/* Submit Button */}
            <button
              type="submit"
              disabled={loading}
              className="w-full py-4 rounded-xl font-semibold text-white
                       bg-gradient-to-r from-cyan-500 to-purple-500 
                       hover:from-cyan-400 hover:to-purple-400
                       disabled:opacity-50 disabled:cursor-not-allowed
                       transform hover:scale-[1.02] active:scale-[0.98]
                       transition-all duration-300 shadow-lg shadow-cyan-500/25
                       flex items-center justify-center gap-2 group"
            >
              {loading ? (
                <FaSpinner className="animate-spin" />
              ) : (
                <>
                  {isLogin ? 'Sign In' : 'Create Account'}
                  <FaArrowRight className="group-hover:translate-x-1 transition-transform" />
                </>
              )}
            </button>
          </form>

          {/* Divider */}
          <div className="flex items-center gap-4 my-8">
            <div className="flex-1 h-px bg-gradient-to-r from-transparent via-gray-700 to-transparent" />
            <span className="text-gray-500 text-sm">or continue with</span>
            <div className="flex-1 h-px bg-gradient-to-r from-transparent via-gray-700 to-transparent" />
          </div>

          {/* Google OAuth */}
          <button
            onClick={handleGoogleLogin}
            className="w-full py-4 rounded-xl font-medium text-white
                     bg-dark/50 border border-gray-700 hover:border-cyan-500/50
                     hover:bg-dark/80 transform hover:scale-[1.02] active:scale-[0.98]
                     transition-all duration-300 flex items-center justify-center gap-3 group"
          >
            <FaGoogle className="text-xl text-red-500 group-hover:scale-110 transition-transform" />
            <span>Continue with Google</span>
          </button>

          {/* Terms */}
          {!isLogin && (
            <p className="mt-6 text-center text-xs text-gray-500">
              By signing up, you agree to our{' '}
              <a href="#" className="text-cyan-400 hover:underline">Terms</a>
              {' '}and{' '}
              <a href="#" className="text-cyan-400 hover:underline">Privacy Policy</a>
            </p>
          )}
        </div>

        {/* Features */}
        <div className="mt-8 flex justify-center gap-6 animate-fade-in" style={{ animationDelay: '0.3s' }}>
          {['AI Summaries', 'Smart Quizzes', 'Video Creation'].map((feature, i) => (
            <div key={feature} className="flex items-center gap-2 text-gray-500 text-sm">
              <HiSparkles className="text-cyan-400" />
              {feature}
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
