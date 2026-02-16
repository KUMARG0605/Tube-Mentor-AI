/**
 * ContentTools - Phase 3 Content Generation UI
 * Provides script, slides, voice, and video generation tools
 */

import { useState } from 'react'
import { toast } from 'react-hot-toast'
import { 
  FaFileAlt, FaFilePowerpoint, FaImage, FaMicrophone, FaVideo,
  FaSpinner, FaDownload, FaCopy, FaPlay
} from 'react-icons/fa'
import {
  generateScript, generateSlides, downloadSlides,
  getImagesForVideo, generateVoiceFromVideo, downloadVoice,
  generateVideo, downloadVideo, getContentStatus
} from '../services/api'


export default function ContentTools({ videoId, hasTranscript, hasSummary }) {
  const [activeTab, setActiveTab] = useState(null)
  const [loading, setLoading] = useState({})
  const [script, setScript] = useState(null)
  const [slides, setSlides] = useState(null)
  const [images, setImages] = useState([])
  const [voice, setVoice] = useState(null)
  const [video, setVideo] = useState(null)

  const setLoadingState = (key, value) => {
    setLoading(prev => ({ ...prev, [key]: value }))
  }

  const handleGenerateScript = async () => {
    if (!hasSummary) {
      toast.error('Generate summary first!')
      return
    }
    setLoadingState('script', true)
    setActiveTab('script')
    try {
      const { data } = await generateScript(videoId)
      setScript(data)
      toast.success('Script generated!')
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Failed to generate script')
    } finally {
      setLoadingState('script', false)
    }
  }

  const handleGenerateSlides = async () => {
    if (!hasSummary) {
      toast.error('Generate summary first!')
      return
    }
    setLoadingState('slides', true)
    setActiveTab('slides')
    try {
      const { data } = await generateSlides(videoId)
      setSlides(data)
      toast.success(`Presentation created with ${data.slide_count} slides!`)
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Failed to generate slides')
    } finally {
      setLoadingState('slides', false)
    }
  }

  const handleGetImages = async () => {
    if (!hasSummary) {
      toast.error('Generate summary first!')
      return
    }
    setLoadingState('images', true)
    setActiveTab('images')
    try {
      const { data } = await getImagesForVideo(videoId)
      setImages(data)
      toast.success(`Found ${data.length} relevant images!`)
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Failed to find images')
    } finally {
      setLoadingState('images', false)
    }
  }

  const handleGenerateVoice = async () => {
    if (!hasSummary) {
      toast.error('Generate summary first!')
      return
    }
    setLoadingState('voice', true)
    setActiveTab('voice')
    try {
      const { data } = await generateVoiceFromVideo(videoId)
      if (data.success) {
        setVoice(data)
        toast.success('Voice narration generated!')
      } else {
        toast.error(data.error || 'Voice generation failed')
      }
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Failed to generate voice')
    } finally {
      setLoadingState('voice', false)
    }
  }

  const handleGenerateVideo = async () => {
    if (!hasSummary) {
      toast.error('Generate summary first!')
      return
    }
    setLoadingState('video', true)
    setActiveTab('video')
    try {
      const { data } = await generateVideo(videoId, false)
      if (data.success) {
        setVideo(data)
        toast.success('Video generated!')
      } else {
        toast.error('Video generation failed')
      }
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Failed to generate video')
    } finally {
      setLoadingState('video', false)
    }
  }

  const copyToClipboard = (text) => {
    navigator.clipboard.writeText(text)
    toast.success('Copied to clipboard!')
  }

  if (!hasTranscript) {
    return null
  }

  return (
    <div className="bg-secondary rounded-xl p-6 mt-6">
      <div className="flex items-center gap-2 mb-4">
        <span className="text-xs bg-primary/20 text-primary px-2 py-1 rounded-full">
          Phase 3
        </span>
        <h2 className="text-lg font-semibold text-white">Content Generation</h2>
      </div>

      {/* Tool Buttons */}
      <div className="flex flex-wrap gap-3 mb-6">
        <ToolButton
          icon={<FaFileAlt />}
          label="Script"
          onClick={handleGenerateScript}
          loading={loading.script}
          disabled={!hasSummary}
          active={activeTab === 'script'}
        />
        <ToolButton
          icon={<FaFilePowerpoint />}
          label="Slides"
          onClick={handleGenerateSlides}
          loading={loading.slides}
          disabled={!hasSummary}
          active={activeTab === 'slides'}
        />
        <ToolButton
          icon={<FaImage />}
          label="Images"
          onClick={handleGetImages}
          loading={loading.images}
          disabled={!hasSummary}
          active={activeTab === 'images'}
        />
        <ToolButton
          icon={<FaMicrophone />}
          label="Voice"
          onClick={handleGenerateVoice}
          loading={loading.voice}
          disabled={!hasSummary}
          active={activeTab === 'voice'}
        />
        <ToolButton
          icon={<FaVideo />}
          label="Video"
          onClick={handleGenerateVideo}
          loading={loading.video}
          disabled={!hasSummary}
          active={activeTab === 'video'}
        />
      </div>

      {/* Content Area */}
      {activeTab === 'script' && script && (
        <div className="bg-dark rounded-lg p-4">
          <div className="flex justify-between items-center mb-3">
            <h3 className="text-white font-medium">Generated Script</h3>
            <button
              onClick={() => copyToClipboard(script.script)}
              className="text-gray-400 hover:text-primary"
            >
              <FaCopy />
            </button>
          </div>
          <div className="text-sm text-gray-300 whitespace-pre-wrap max-h-96 overflow-y-auto">
            {script.script}
          </div>
          <div className="mt-3 text-xs text-gray-500">
            {script.word_count} words • ~{script.estimated_duration_minutes} min
          </div>
        </div>
      )}

      {activeTab === 'slides' && slides && (
        <div className="bg-dark rounded-lg p-4">
          <div className="flex justify-between items-center mb-3">
            <h3 className="text-white font-medium">{slides.title}</h3>
            <a
              href={downloadSlides(slides.filename)}
              className="flex items-center gap-2 px-4 py-2 bg-primary text-white 
                         rounded-lg hover:bg-primary/80 transition-colors"
            >
              <FaDownload />
              Download PPTX
            </a>
          </div>
          <p className="text-gray-400 text-sm">
            {slides.slide_count} slides created
          </p>
        </div>
      )}

      {activeTab === 'images' && images.length > 0 && (
        <div className="bg-dark rounded-lg p-4">
          <h3 className="text-white font-medium mb-3">Relevant Images</h3>
          <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
            {images.map((img) => (
              <a
                key={img.id}
                href={img.urls.full}
                target="_blank"
                rel="noopener noreferrer"
                className="group relative rounded-lg overflow-hidden aspect-video"
              >
                <img
                  src={img.urls.small}
                  alt={img.description}
                  className="w-full h-full object-cover group-hover:scale-105 transition-transform"
                />
                <div className="absolute bottom-0 left-0 right-0 bg-black/70 p-2 
                                opacity-0 group-hover:opacity-100 transition-opacity">
                  <p className="text-xs text-white truncate">{img.attribution}</p>
                </div>
              </a>
            ))}
          </div>
        </div>
      )}

      {activeTab === 'voice' && voice && (
        <div className="bg-dark rounded-lg p-4">
          <div className="flex justify-between items-center mb-3">
            <h3 className="text-white font-medium">Voice Narration</h3>
            <a
              href={downloadVoice(voice.filename)}
              className="flex items-center gap-2 px-4 py-2 bg-primary text-white 
                         rounded-lg hover:bg-primary/80 transition-colors"
            >
              <FaDownload />
              Download MP3
            </a>
          </div>
          <audio controls className="w-full mt-2">
            <source src={downloadVoice(voice.filename)} type="audio/mpeg" />
          </audio>
          <p className="text-gray-400 text-sm mt-2">
            Duration: ~{Math.round(voice.duration_seconds)}s
          </p>
        </div>
      )}

      {activeTab === 'video' && video && (
        <div className="bg-dark rounded-lg p-4">
          <div className="flex justify-between items-center mb-3">
            <h3 className="text-white font-medium">Generated Video</h3>
            <a
              href={downloadVideo(video.filename)}
              className="flex items-center gap-2 px-4 py-2 bg-primary text-white 
                         rounded-lg hover:bg-primary/80 transition-colors"
            >
              <FaDownload />
              Download MP4
            </a>
          </div>
          <video controls className="w-full rounded-lg mt-2">
            <source src={downloadVideo(video.filename)} type="video/mp4" />
          </video>
          <p className="text-gray-400 text-sm mt-2">
            Duration: {Math.round(video.duration_seconds)}s
          </p>
        </div>
      )}

      {/* Loading State */}
      {Object.values(loading).some(Boolean) && !script && !slides && !images.length && !voice && !video && (
        <div className="flex items-center justify-center py-8">
          <FaSpinner className="animate-spin text-primary text-xl mr-2" />
          <span className="text-gray-400">Generating content...</span>
        </div>
      )}

      {/* Hint when no summary */}
      {!hasSummary && (
        <p className="text-gray-500 text-sm text-center">
          Generate a summary first to unlock content creation tools
        </p>
      )}
    </div>
  )
}


function ToolButton({ icon, label, onClick, loading, disabled, active }) {
  return (
    <button
      onClick={onClick}
      disabled={loading || disabled}
      className={`flex items-center gap-2 px-4 py-2 rounded-lg transition-all
                  ${active 
                    ? 'bg-primary text-white' 
                    : 'bg-dark text-gray-300 hover:bg-dark/80'}
                  ${disabled ? 'opacity-40 cursor-not-allowed' : ''}`}
    >
      {loading ? <FaSpinner className="animate-spin" /> : icon}
      {label}
    </button>
  )
}
