import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import { FaSpinner, FaCheck, FaTimes } from 'react-icons/fa'

export default function AuthCallback() {
  const [status, setStatus] = useState('processing')
  const [error, setError] = useState('')
  const { loginWithGoogle } = useAuth()
  const navigate = useNavigate()

  useEffect(() => {
    handleCallback()
  }, [])

  const handleCallback = async () => {
    // Parse the hash fragment for OAuth tokens
    const hash = window.location.hash.substring(1)
    const params = new URLSearchParams(hash)
    const accessToken = params.get('access_token')
    const error = params.get('error')

    if (error) {
      setStatus('error')
      setError('Authentication was cancelled or failed')
      return
    }

    if (!accessToken) {
      setStatus('error')
      setError('No access token received')
      return
    }

    try {
      await loginWithGoogle(accessToken)
      setStatus('success')
      setTimeout(() => navigate('/'), 2000)
    } catch (err) {
      setStatus('error')
      setError(err.message || 'Failed to authenticate with Google')
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center px-4">
      <div className="text-center animate-fade-in">
        {status === 'processing' && (
          <>
            <FaSpinner className="text-5xl text-cyan-400 mx-auto mb-4 animate-spin" />
            <h2 className="text-xl font-semibold text-white mb-2">Signing you in...</h2>
            <p className="text-gray-400">Please wait while we complete your authentication</p>
          </>
        )}
        
        {status === 'success' && (
          <>
            <div className="w-16 h-16 rounded-full bg-green-500/20 flex items-center justify-center mx-auto mb-4 animate-bounce-in">
              <FaCheck className="text-3xl text-green-400" />
            </div>
            <h2 className="text-xl font-semibold text-white mb-2">Welcome!</h2>
            <p className="text-gray-400">Redirecting you to the app...</p>
          </>
        )}
        
        {status === 'error' && (
          <>
            <div className="w-16 h-16 rounded-full bg-red-500/20 flex items-center justify-center mx-auto mb-4 animate-bounce-in">
              <FaTimes className="text-3xl text-red-400" />
            </div>
            <h2 className="text-xl font-semibold text-white mb-2">Authentication Failed</h2>
            <p className="text-gray-400 mb-4">{error}</p>
            <button
              onClick={() => navigate('/login')}
              className="px-6 py-3 bg-gradient-to-r from-cyan-500 to-purple-500 text-white rounded-xl
                       hover:from-cyan-400 hover:to-purple-400 transition-all"
            >
              Try Again
            </button>
          </>
        )}
      </div>
    </div>
  )
}
