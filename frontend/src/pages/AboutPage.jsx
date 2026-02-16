import { useState, useEffect } from 'react'
import { FaBrain, FaYoutube, FaRobot, FaFilePdf, FaQuestionCircle, FaLightbulb, FaRocket, FaCheck, FaClock } from 'react-icons/fa'

export default function AboutPage() {
  const [phases, setPhases] = useState(null)

  useEffect(() => {
    fetch('http://localhost:8000/')
      .then(res => res.json())
      .then(data => setPhases(data.phases))
      .catch(() => {})
  }, [])

  const allPhases = [
    {
      id: 'phase1_core',
      name: 'Phase 1: Core Agent',
      description: 'YouTube search, transcript extraction, AI summaries, quizzes, and PDF export.',
      features: ['YouTube Search', 'Transcript Fetch', 'AI Summary', 'Quiz Generation', 'PDF Export'],
      icon: <FaBrain />,
    },
    {
      id: 'phase2_intelligence',
      name: 'Phase 2: Intelligence',
      description: 'Vector embeddings, FAISS similarity search, and AI-powered recommendations.',
      features: ['SentenceTransformers', 'FAISS Vector DB', 'Similar Videos', 'Semantic Search'],
      icon: <FaRobot />,
    },
    {
      id: 'phase3_content',
      name: 'Phase 3: Content Generation',
      description: 'Create scripts, presentations, images, voice narration, and videos from video content.',
      features: ['Script (Groq)', 'Slides (PPTX)', 'Images (Unsplash)', 'Voice (ElevenLabs)', 'Video (MoviePy)'],
      icon: <FaLightbulb />,
    },
    {
      id: 'phase4_multimodal',
      name: 'Phase 4: Multimodal',
      description: 'Video frame analysis, visual Q&A, and advanced content understanding.',
      features: ['Frame Extraction', 'Visual AI', 'Diagram Analysis', 'Multi-modal Q&A'],
      icon: <FaRocket />,
    },
  ]

  return (
    <div className="max-w-4xl mx-auto py-8 px-4">
      {/* Hero */}
      <div className="text-center mb-12">
        <div className="flex items-center justify-center gap-3 mb-4">
          <FaBrain className="text-primary text-4xl" />
          <h1 className="text-3xl font-bold">
            <span className="text-primary">Tube</span>
            <span className="text-white">Mentor</span>
            <span className="text-primary/60 ml-2 text-xl">AI</span>
          </h1>
        </div>
        <p className="text-gray-400 text-lg max-w-2xl mx-auto">
          Your AI-powered YouTube learning assistant. Search videos, get AI summaries, 
          generate quizzes, and export study notes — all in one place.
        </p>
      </div>

      {/* Features Grid */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-12">
        {[
          { icon: <FaYoutube className="text-red-500" />, label: 'YouTube Search' },
          { icon: <FaLightbulb className="text-yellow-500" />, label: 'AI Summaries' },
          { icon: <FaQuestionCircle className="text-blue-500" />, label: 'Smart Quizzes' },
          { icon: <FaFilePdf className="text-primary" />, label: 'PDF Export' },
        ].map((f, i) => (
          <div key={i} className="bg-secondary rounded-xl p-4 text-center">
            <div className="text-2xl mb-2">{f.icon}</div>
            <div className="text-sm text-gray-300">{f.label}</div>
          </div>
        ))}
      </div>

      {/* Phases Roadmap */}
      <h2 className="text-xl font-semibold text-white mb-6 flex items-center gap-2">
        <FaRocket className="text-primary" />
        Development Phases
      </h2>

      <div className="space-y-4">
        {allPhases.map((phase, idx) => {
          const isActive = phases?.[phase.id] || false
          return (
            <div
              key={phase.id}
              className={`bg-secondary rounded-xl p-5 border-l-4 transition-all ${
                isActive ? 'border-primary' : 'border-gray-700'
              }`}
            >
              <div className="flex items-start gap-4">
                <div className={`p-3 rounded-lg ${isActive ? 'bg-primary/20 text-primary' : 'bg-dark text-gray-500'}`}>
                  {phase.icon}
                </div>
                <div className="flex-1">
                  <div className="flex items-center gap-3 mb-2">
                    <h3 className="font-semibold text-white">{phase.name}</h3>
                    {isActive ? (
                      <span className="flex items-center gap-1 text-xs bg-green-500/20 text-green-400 px-2 py-0.5 rounded-full">
                        <FaCheck size={10} /> Active
                      </span>
                    ) : (
                      <span className="flex items-center gap-1 text-xs bg-gray-700 text-gray-400 px-2 py-0.5 rounded-full">
                        <FaClock size={10} /> Coming Soon
                      </span>
                    )}
                  </div>
                  <p className="text-gray-400 text-sm mb-3">{phase.description}</p>
                  <div className="flex flex-wrap gap-2">
                    {phase.features.map((f, fi) => (
                      <span
                        key={fi}
                        className={`text-xs px-2 py-1 rounded ${
                          isActive ? 'bg-primary/10 text-primary' : 'bg-dark text-gray-500'
                        }`}
                      >
                        {f}
                      </span>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          )
        })}
      </div>

      {/* Tech Stack */}
      <div className="mt-12 bg-secondary rounded-xl p-6">
        <h2 className="text-lg font-semibold text-white mb-4">Tech Stack</h2>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
          <div>
            <div className="text-primary font-medium mb-1">Backend</div>
            <div className="text-gray-400">FastAPI, PostgreSQL, SQLAlchemy</div>
          </div>
          <div>
            <div className="text-primary font-medium mb-1">Frontend</div>
            <div className="text-gray-400">React, Vite, Tailwind CSS</div>
          </div>
          <div>
            <div className="text-primary font-medium mb-1">AI/ML</div>
            <div className="text-gray-400">Groq LLM, SentenceTransformers</div>
          </div>
          <div>
            <div className="text-primary font-medium mb-1">Vector DB</div>
            <div className="text-gray-400">FAISS (Similarity Search)</div>
          </div>
        </div>
      </div>

      {/* Footer */}
      <div className="mt-8 text-center text-gray-500 text-sm">
        Built for learning • Open Source
      </div>
    </div>
  )
}
