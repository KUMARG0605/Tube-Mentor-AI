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
  API.get(`/recommendations/similar/${videoId}?limit=${limit}`)

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

export default API
