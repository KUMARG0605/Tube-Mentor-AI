import { useState, useEffect } from 'react'
import { useParams, Link } from 'react-router-dom'
import ReactMarkdown from 'react-markdown'
import toast from 'react-hot-toast'
import {
  FaArrowLeft,
  FaFileAlt,
  FaLightbulb,
  FaQuestionCircle,
  FaFilePdf,
  FaDownload,
  FaSpinner,
  FaThumbsUp,
} from 'react-icons/fa'

import QuizCard from '../components/QuizCard'
import LoadingSpinner from '../components/LoadingSpinner'
import ContentTools from '../components/ContentTools'
import { fetchTranscript, generateSummary, generateQuiz, generatePDF, downloadPDF, indexVideo, getSimilarVideos } from '../services/api'

export default function VideoPage() {
  const { videoId } = useParams()

  // Tab and content state
  const [activeTab, setActiveTab] = useState('transcript')
  const [transcript, setTranscript] = useState(null)
  const [summary, setSummary] = useState(null)
  const [quiz, setQuiz] = useState(null)
  const [pdfInfo, setPdfInfo] = useState(null)
  
  // AI recommendations state
  const [recommendations, setRecommendations] = useState([])
  const [loadingRecommendations, setLoadingRecommendations] = useState(false)

  // Loading states
  const [loadingTranscript, setLoadingTranscript] = useState(false)
  const [loadingSummary, setLoadingSummary] = useState(false)
  const [loadingQuiz, setLoadingQuiz] = useState(false)
  const [loadingPDF, setLoadingPDF] = useState(false)

  const youtubeUrl = `https://www.youtube.com/embed/${videoId}`

  // Auto-fetch transcript on mount/videoId change
  useEffect(() => {
    handleFetchTranscript()
  }, [videoId])

  const handleFetchTranscript = async () => {
    setLoadingTranscript(true)
    try {
      const { data } = await fetchTranscript(videoId)
      setTranscript(data)
      toast.success('Transcript loaded!')
      // Fetch recommendations from already indexed videos (don't index yet)
      fetchRecommendationsOnly()
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Failed to fetch transcript.')
    } finally {
      setLoadingTranscript(false)
    }
  }

  // Fetch similar videos without indexing current video
  const fetchRecommendationsOnly = async () => {
    setLoadingRecommendations(true)
    try {
      const { data } = await getSimilarVideos(videoId, 5)
      const filteredRecommendations = data.recommendations?.filter(
        rec => rec.video_id !== videoId
      ) || []
      setRecommendations(filteredRecommendations)
    } catch (err) {
      // Video not indexed yet - that's OK, will be indexed after summary
      console.log('Recommendations not available yet:', err.message)
      setRecommendations([])
    } finally {
      setLoadingRecommendations(false)
    }
  }

  // Index video AFTER summary is generated (richer content for better matching)
  const handleIndexAndFetchRecommendations = async () => {
    setLoadingRecommendations(true)
    try {
      await indexVideo(videoId)
      const { data } = await getSimilarVideos(videoId, 5)
      const filteredRecommendations = data.recommendations?.filter(
        rec => rec.video_id !== videoId
      ) || []
      setRecommendations(filteredRecommendations)
    } catch (err) {
      console.log('Recommendations not available:', err.message)
      setRecommendations([])
    } finally {
      setLoadingRecommendations(false)
    }
  }

  const handleGenerateSummary = async () => {
    if (!transcript) {
      toast.error('Fetch transcript first!')
      return
    }
    setLoadingSummary(true)
    setActiveTab('summary')
    try {
      const { data } = await generateSummary(videoId)
      setSummary(data)
      toast.success('Summary generated!')
      
      // Index video with rich content (summary) for better recommendations
      // This happens after summary so we have better content for similarity matching
      handleIndexAndFetchRecommendations()
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Summary generation failed.')
    } finally {
      setLoadingSummary(false)
    }
  }

  const handleGenerateQuiz = async () => {
    if (!transcript) {
      toast.error('Fetch transcript first!')
      return
    }
    setLoadingQuiz(true)
    setActiveTab('quiz')
    try {
      const { data } = await generateQuiz(videoId)
      setQuiz(data)
      toast.success('Quiz generated!')
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Quiz generation failed.')
    } finally {
      setLoadingQuiz(false)
    }
  }

  const handleGeneratePDF = async () => {
    if (!summary && !quiz) {
      toast.error('Generate a summary or quiz first!')
      return
    }
    setLoadingPDF(true)
    try {
      const { data } = await generatePDF(videoId, !!summary, !!quiz)
      setPdfInfo(data)
      toast.success('PDF generated!')
    } catch (err) {
      toast.error(err.response?.data?.detail || 'PDF generation failed.')
    } finally {
      setLoadingPDF(false)
    }
  }

  const tabs = [
    { key: 'transcript', label: 'Transcript', icon: <FaFileAlt /> },
    { key: 'summary', label: 'Summary', icon: <FaLightbulb /> },
    { key: 'quiz', label: 'Quiz', icon: <FaQuestionCircle /> },
  ]

  return (
    <div className="max-w-7xl mx-auto px-4 py-6">
      <Link to="/" className="inline-flex items-center gap-2 text-gray-400 hover:text-primary text-sm mb-4 transition-colors">
        <FaArrowLeft /> Back to Search
      </Link>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Video Player */}
        <div className="lg:col-span-2">
          <div className="aspect-video rounded-xl overflow-hidden border border-gray-800">
            <iframe
              src={youtubeUrl}
              title="YouTube Video"
              className="w-full h-full"
              allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
              allowFullScreen
            />
          </div>

          {/* Action Buttons */}
          <div className="flex flex-wrap gap-3 mt-4">
            <ActionBtn
              onClick={handleGenerateSummary}
              loading={loadingSummary}
              icon={<FaLightbulb />}
              label="Generate Summary"
              disabled={!transcript}
            />
            <ActionBtn
              onClick={handleGenerateQuiz}
              loading={loadingQuiz}
              icon={<FaQuestionCircle />}
              label="Generate Quiz"
              disabled={!transcript}
            />
            <ActionBtn
              onClick={handleGeneratePDF}
              loading={loadingPDF}
              icon={<FaFilePdf />}
              label="Generate PDF"
              disabled={!summary && !quiz}
            />
            {pdfInfo && (
              <a
                href={downloadPDF(pdfInfo.file_name)}
                target="_blank"
                rel="noopener noreferrer"
                className="flex items-center gap-2 px-4 py-2 bg-green-600 hover:bg-green-700 
                           text-white text-sm rounded-lg transition-colors"
              >
                <FaDownload /> Download PDF
              </a>
            )}
          </div>
        </div>

        {/* Content Panel */}
        <div className="lg:col-span-1">
          {/* Tab Navigation */}
          <div className="flex border-b border-gray-800 mb-4">
            {tabs.map((tab) => (
              <button
                key={tab.key}
                onClick={() => setActiveTab(tab.key)}
                className={`flex items-center gap-1.5 px-4 py-2.5 text-xs font-medium transition-colors
                  ${activeTab === tab.key
                    ? 'text-primary border-b-2 border-primary'
                    : 'text-gray-500 hover:text-gray-300'
                  }`}
              >
                {tab.icon} {tab.label}
              </button>
            ))}
          </div>

          {/* Tab Content */}
          <div className="bg-dark rounded-xl border border-gray-800 p-4 max-h-[70vh] overflow-y-auto">
            {/* Transcript Tab */}
            {activeTab === 'transcript' && (
              loadingTranscript ? (
                <LoadingSpinner text="Fetching transcript..." />
              ) : transcript ? (
                <div>
                  <div className="flex items-center justify-between mb-3">
                    <span className="text-xs text-gray-500">{transcript.word_count} words</span>
                    <span className="text-xs text-gray-500">Language: {transcript.language}</span>
                  </div>
                  <p className="text-sm text-gray-300 leading-relaxed whitespace-pre-wrap">
                    {transcript.content}
                  </p>
                </div>
              ) : (
                <p className="text-gray-500 text-sm text-center py-8">
                  No transcript available for this video.
                </p>
              )
            )}

            {/* Summary Tab */}
            {activeTab === 'summary' && (
              loadingSummary ? (
                <LoadingSpinner text="AI is summarizing..." />
              ) : summary ? (
                <div>
                  {summary.key_topics?.length > 0 && (
                    <div className="flex flex-wrap gap-1.5 mb-4">
                      {summary.key_topics.map((t, i) => (
                        <span key={i} className="px-2 py-0.5 bg-primary/10 text-primary text-xs rounded-full">
                          {t}
                        </span>
                      ))}
                    </div>
                  )}
                  <div className="markdown-body text-sm text-gray-300">
                    <ReactMarkdown>{summary.summary_text}</ReactMarkdown>
                  </div>
                </div>
              ) : (
                <p className="text-gray-500 text-sm text-center py-8">
                  Click "Generate Summary" to get AI-powered notes.
                </p>
              )
            )}

            {/* Quiz Tab */}
            {activeTab === 'quiz' && (
              loadingQuiz ? (
                <LoadingSpinner text="AI is generating quiz..." />
              ) : quiz ? (
                <QuizCard questions={quiz.questions} />
              ) : (
                <p className="text-gray-500 text-sm text-center py-8">
                  Click "Generate Quiz" to test your knowledge.
                </p>
              )
            )}
          </div>
        </div>
      </div>

      {/* Similar Videos Section - Always show after transcript */}
      {transcript && (
        <div className="mt-8 mb-8">
          <div className="bg-secondary rounded-xl p-6">
            <div className="flex items-center gap-2 mb-4">
              <FaThumbsUp className="text-primary" />
              <h2 className="text-lg font-semibold text-white">
                Similar Videos You Might Like
              </h2>
              <span className="text-xs text-gray-400 ml-2">
                Powered by AI
              </span>
            </div>

            {loadingRecommendations ? (
              <div className="flex items-center justify-center py-8">
                <FaSpinner className="animate-spin text-primary text-xl mr-2" />
                <span className="text-gray-400">Finding similar videos...</span>
              </div>
            ) : recommendations.length > 0 ? (
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
                {recommendations.map((rec) => (
                  <Link
                    key={rec.video_id}
                    to={`/video/${rec.video_id}`}
                    className="bg-dark rounded-lg overflow-hidden hover:ring-2 
                               hover:ring-primary transition-all group"
                  >
                    <div className="relative aspect-video">
                      <img
                        src={`https://img.youtube.com/vi/${rec.video_id}/mqdefault.jpg`}
                        alt={rec.title || 'Video thumbnail'}
                        className="w-full h-full object-cover group-hover:opacity-80 transition-opacity"
                      />
                      <div className="absolute top-2 right-2 bg-primary/90 text-white 
                                      text-xs px-2 py-1 rounded-full font-medium">
                        {Math.round(rec.similarity_score * 100)}% match
                      </div>
                    </div>
                    <div className="p-3">
                      <h3 className="text-sm text-white font-medium line-clamp-2 
                                     group-hover:text-primary transition-colors">
                        {rec.title || `Video ${rec.video_id}`}
                      </h3>
                      {rec.channel_title && (
                        <p className="text-xs text-gray-400 mt-1">
                          {rec.channel_title}
                        </p>
                      )}
                    </div>
                  </Link>
                ))}
              </div>
            ) : (
              <p className="text-gray-500 text-sm text-center py-4">
                No similar videos found yet. Watch more videos to get personalized recommendations!
              </p>
            )}
          </div>
        </div>
      )}

      {/* Phase 3: Content Generation Tools */}
      <ContentTools
        videoId={videoId}
        hasTranscript={!!transcript}
        hasSummary={!!summary}
      />
    </div>
  )
}

// Reusable action button component
function ActionBtn({ onClick, loading, icon, label, disabled }) {
  return (
    <button
      onClick={onClick}
      disabled={loading || disabled}
      className="flex items-center gap-2 px-4 py-2 bg-accent hover:bg-accent/80 
                 text-white text-sm rounded-lg transition-colors
                 disabled:opacity-40 disabled:cursor-not-allowed"
    >
      {loading ? <FaSpinner className="animate-spin" /> : icon}
      {label}
    </button>
  )
}
