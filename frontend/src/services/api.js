/**
 * TubeMentor AI - API Service Layer
 * Centralized API communication for frontend-backend interaction
 */

import axios from 'axios'

const API = axios.create({
  baseURL: '/api',
  headers: { 'Content-Type': 'application/json' },
})

// Search API
/**
 * @param {string} query - Search term
 * @param {number} maxResults - Maximum videos to return (default: 10)
 * @returns {Promise} - Search results
 */
export const searchVideos = (query, maxResults = 10) =>
  API.post('/search/', { query, max_results: maxResults })

/**
 * @param {number} limit - Max history items (default: 20)
 * @returns {Promise} - Previous searches
 */
export const getSearchHistory = (limit = 20) =>
  API.get(`/search/history?limit=${limit}`)

// Transcript API
/**
 * @param {string} videoId - YouTube video ID
 * @param {string} language - Language code (default: 'en')
 * @returns {Promise} - Video transcript with timestamps
 */
export const fetchTranscript = (videoId, language = 'en') =>
  API.post('/transcript/', { video_id: videoId, language })

/**
 * @param {string} videoId - YouTube video ID
 * @returns {Promise} - Saved transcript
 */
export const getTranscript = (videoId) =>
  API.get(`/transcript/${videoId}`)

// Summary API
/**
 * @param {string} videoId - YouTube video ID
 * @returns {Promise} - AI-generated summary
 */
export const generateSummary = (videoId) =>
  API.post('/summary/', { video_id: videoId })

/**
 * @param {string} videoId - YouTube video ID
 * @returns {Promise} - Saved summary
 */
export const getSummary = (videoId) =>
  API.get(`/summary/${videoId}`)

// Quiz API
/**
 * @param {string} videoId - YouTube video ID
 * @param {number} numQuestions - Number of questions (default: 5)
 * @returns {Promise} - AI-generated MCQ quiz
 */
export const generateQuiz = (videoId, numQuestions = 5) =>
  API.post('/quiz/', { video_id: videoId, num_questions: numQuestions })

/**
 * @param {string} videoId - YouTube video ID
 * @returns {Promise} - Saved quiz
 */
export const getQuiz = (videoId) =>
  API.get(`/quiz/${videoId}`)

// PDF API
/**
 * @param {string} videoId - YouTube video ID
 * @param {boolean} includeSummary - Include summary section (default: true)
 * @param {boolean} includeQuiz - Include quiz section (default: true)
 * @returns {Promise} - PDF generation result with download filename
 */
export const generatePDF = (videoId, includeSummary = true, includeQuiz = true) =>
  API.post('/pdf/', {
    video_id: videoId,
    include_summary: includeSummary,
    include_quiz: includeQuiz,
  })

/**
 * @param {string} fileName - PDF filename from generatePDF response
 * @returns {string} - Full URL for downloading the PDF
 */
export const downloadPDF = (fileName) =>
  `${window.location.origin}/api/pdf/download/${fileName}`

// Recommendations API
/**
 * @param {string} videoId - YouTube video ID to index
 * @returns {Promise} - Indexing result
 */
export const indexVideo = (videoId) =>
  API.post('/recommendations/index', { video_id: videoId })

/**
 * @param {string} videoId - YouTube video ID
 * @param {number} limit - Maximum results (default: 5)
 * @returns {Promise} - Similar videos with similarity scores
 */
export const getSimilarVideos = (videoId, limit = 5) =>
  API.get(`/recommendations/similar/${videoId}?k=${limit}`)

/**
 * @param {string} query - Natural language search query
 * @param {number} limit - Maximum results (default: 5)
 * @returns {Promise} - Videos matching semantic meaning
 */
export const semanticSearch = (query, limit = 5) =>
  API.get(`/recommendations/search?q=${encodeURIComponent(query)}&limit=${limit}`)

/**
 * @returns {Promise} - Vector store statistics
 */
export const getRecommendationStats = () =>
  API.get('/recommendations/stats')

// ============== Phase 3: Content Generation ==============

/**
 * Generate video script from existing video content
 * @param {string} videoId - YouTube video ID
 * @param {number} duration - Target duration in minutes
 * @returns {Promise} - Generated script
 */
export const generateScript = (videoId, duration = 10) =>
  API.post('/content/script/from-video', { video_id: videoId, duration })

/**
 * Generate custom script on any topic
 * @param {string} topic - Topic for the script
 * @param {string} style - Script style (educational, casual, formal)
 * @param {number} duration - Target duration in minutes
 * @returns {Promise} - Generated script
 */
export const generateCustomScript = (topic, style = 'educational', duration = 10) =>
  API.post('/content/script/custom', { topic, style, duration })

/**
 * Generate PowerPoint slides from video summary
 * @param {string} videoId - YouTube video ID
 * @returns {Promise} - Slides file info
 */
export const generateSlides = (videoId) =>
  API.post('/content/slides', { video_id: videoId })

/**
 * Download generated slides
 * @param {string} filename - Slides filename
 * @returns {string} - Download URL
 */
export const downloadSlides = (filename) =>
  `${window.location.origin}/api/content/slides/download/${filename}`

/**
 * Search for relevant images
 * @param {string} query - Search keywords
 * @param {number} count - Number of images
 * @returns {Promise} - Image results
 */
export const searchImages = (query, count = 5) =>
  API.post('/content/images/search', { query, count })

/**
 * Get images for a video based on its content
 * @param {string} videoId - YouTube video ID
 * @returns {Promise} - Relevant images
 */
export const getImagesForVideo = (videoId) =>
  API.get(`/content/images/for-video/${videoId}`)

/**
 * Get available voice options
 * @returns {Promise} - Voice list
 */
export const getVoices = () =>
  API.get('/content/voice/voices')

/**
 * Generate text-to-speech audio
 * @param {string} text - Text to convert
 * @param {string} voiceId - Voice ID (optional)
 * @returns {Promise} - Audio file info
 */
export const generateVoice = (text, voiceId = null) =>
  API.post('/content/voice/generate', { text, voice_id: voiceId })

/**
 * Generate voice narration from video summary
 * @param {string} videoId - YouTube video ID
 * @param {string} voiceId - Voice ID (optional)
 * @returns {Promise} - Audio file info
 */
export const generateVoiceFromVideo = (videoId, voiceId = null) =>
  API.post(`/content/voice/from-script/${videoId}${voiceId ? `?voice_id=${voiceId}` : ''}`)

/**
 * Download generated audio
 * @param {string} filename - Audio filename
 * @returns {string} - Download URL
 */
export const downloadVoice = (filename) =>
  `${window.location.origin}/api/content/voice/download/${filename}`

/**
 * Get video generation status
 * @returns {Promise} - Video capability status
 */
export const getVideoStatus = () =>
  API.get('/content/video/status')

/**
 * Generate video from slides and audio
 * @param {string} videoId - YouTube video ID
 * @param {boolean} includeAudio - Include voice narration
 * @returns {Promise} - Video file info
 */
export const generateVideo = (videoId, includeAudio = false) =>
  API.post(`/content/video/generate/${videoId}?include_audio=${includeAudio}`)

/**
 * Download generated video
 * @param {string} filename - Video filename
 * @returns {string} - Download URL
 */
export const downloadVideo = (filename) =>
  `${window.location.origin}/api/content/video/download/${filename}`

/**
 * Get Phase 3 status
 * @returns {Promise} - Content generation capabilities
 */
export const getContentStatus = () =>
  API.get('/content/status')

export default API
