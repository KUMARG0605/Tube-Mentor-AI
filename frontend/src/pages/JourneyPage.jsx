import { 
  FaRoad, FaGraduationCap, FaBrain, FaRocket, FaLightbulb, 
  FaCode, FaHeart, FaStar, FaCheckCircle, FaSpinner, FaCircle,
  FaYoutube, FaRobot, FaChartLine, FaUsers
} from 'react-icons/fa'

const milestones = [
  {
    year: "The Beginning",
    title: "The Idea Sparked",
    description: "It all started when I struggled to take notes while watching educational YouTube videos. I thought - why can't AI do this for me?",
    icon: FaLightbulb,
    color: "from-yellow-400 to-orange-500",
    status: "completed"
  },
  {
    year: "Phase 1",
    title: "Learning Foundation",
    description: "Built the core engine - YouTube video analysis, transcript extraction, AI-powered summaries, and interactive quizzes. The journey of making learning smarter began.",
    icon: FaGraduationCap,
    color: "from-blue-400 to-cyan-500",
    status: "completed",
    features: ["Video Transcript Extraction", "AI Summaries", "Smart Quizzes", "Flashcard Generation"]
  },
  {
    year: "Phase 2",
    title: "Intelligence Layer",
    description: "Added recommendations powered by vector embeddings and FAISS. Now TubeMentor can suggest related videos based on what you're learning.",
    icon: FaBrain,
    color: "from-purple-400 to-pink-500",
    status: "completed",
    features: ["Vector Embeddings", "FAISS Search", "Smart Recommendations", "Similar Content Discovery"]
  },
  {
    year: "Phase 3",
    title: "Content Creation Suite",
    description: "Transforming learning into creating. Generate scripts, slides, add professional voiceovers, and create complete videos from any YouTube content.",
    icon: FaRocket,
    color: "from-primary to-purple-500",
    status: "in-progress",
    features: ["Script Generation", "Slide Creator", "Voice Synthesis (ElevenLabs)", "Video Generation"]
  },
  {
    year: "Phase 4",
    title: "Community & Publishing",
    description: "The final piece - share your creations with the world. Integrated social publishing and community features to spread knowledge.",
    icon: FaUsers,
    color: "from-green-400 to-emerald-500",
    status: "planned",
    features: ["Multi-Platform Publishing", "Community Sharing", "Learning Groups", "Progress Analytics"]
  }
]

const stats = [
  { label: "Lines of Code", value: "15,000+", icon: FaCode },
  { label: "AI Models", value: "5+", icon: FaRobot },
  { label: "Features Built", value: "20+", icon: FaStar },
  { label: "Cups of Coffee", value: "∞", icon: FaHeart }
]

// const techStack = [
//   { name: "React", category: "Frontend" },
//   { name: "Tailwind CSS", category: "Frontend" },
//   { name: "FastAPI", category: "Backend" },
//   { name: "PostgreSQL", category: "Database" },
//   { name: "LLM's", category: "AI" },
//   { name: "FAISS", category: "AI" },
//   { name: "ElevenLabs", category: "AI" },
//   { name: "MoviePy", category: "Media" }
// ]

export default function JourneyPage() {
  return (
    <div className="min-h-screen py-12 px-4">
      {/* Hero Section */}
      <div className="max-w-4xl mx-auto text-center mb-16">
        <div className="inline-flex items-center gap-2 bg-primary/10 px-4 py-2 rounded-full mb-6">
          <FaRoad className="text-primary" />
          <span className="text-sm text-gray-400">The Journey</span>
        </div>
        
        <h1 className="text-4xl md:text-6xl font-bold mb-6">
          <span className="bg-gradient-to-r from-primary via-purple-500 to-pink-500 bg-clip-text text-transparent">
            Building TubeMentor AI
          </span>
        </h1>
        
        <p className="text-xl text-gray-400 max-w-2xl mx-auto mb-8">
          A solo developer's journey to revolutionize learning through AI. 
          From a simple idea to a complete learning ecosystem.
        </p>

        {/* Stats */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {stats.map((stat, index) => (
            <div key={index} className="bg-secondary/50 backdrop-blur rounded-xl p-4 border border-gray-800">
              <stat.icon className="text-2xl text-primary mx-auto mb-2" />
              <div className="text-2xl font-bold text-white">{stat.value}</div>
              <div className="text-xs text-gray-500">{stat.label}</div>
            </div>
          ))}
        </div>
      </div>

      {/* Timeline */}
      <div className="max-w-4xl mx-auto mb-16">
        <div className="relative">
          {/* Vertical line */}
          <div className="absolute left-8 md:left-1/2 top-0 bottom-0 w-0.5 bg-gradient-to-b from-primary via-purple-500 to-gray-800" />

          {milestones.map((milestone, index) => (
            <div 
              key={index}
              className={`relative flex items-start gap-8 mb-12 ${
                index % 2 === 0 ? 'md:flex-row' : 'md:flex-row-reverse'
              }`}
            >
              {/* Timeline dot */}
              <div className="absolute left-8 md:left-1/2 -translate-x-1/2 z-10">
                <div className={`w-16 h-16 rounded-full bg-gradient-to-br ${milestone.color} p-0.5`}>
                  <div className="w-full h-full bg-dark rounded-full flex items-center justify-center">
                    <milestone.icon className="text-xl text-white" />
                  </div>
                </div>
              </div>

              {/* Content */}
              <div className={`ml-24 md:ml-0 md:w-1/2 ${
                index % 2 === 0 ? 'md:pr-16 md:text-right' : 'md:pl-16'
              }`}>
                <div className="bg-secondary/50 backdrop-blur rounded-2xl p-6 border border-gray-800 hover:border-primary/30 transition-all">
                  <div className={`flex items-center gap-2 mb-2 ${
                    index % 2 === 0 ? 'md:justify-end' : ''
                  }`}>
                    <span className={`text-xs px-2 py-1 rounded-full bg-gradient-to-r ${milestone.color}`}>
                      {milestone.year}
                    </span>
                    {milestone.status === 'completed' && (
                      <FaCheckCircle className="text-green-500" />
                    )}
                    {milestone.status === 'in-progress' && (
                      <FaSpinner className="text-yellow-500 animate-spin" />
                    )}
                    {milestone.status === 'planned' && (
                      <FaCircle className="text-gray-500 text-xs" />
                    )}
                  </div>
                  
                  <h3 className="text-xl font-bold text-white mb-2">{milestone.title}</h3>
                  <p className="text-gray-400 text-sm mb-4">{milestone.description}</p>
                  
                  {milestone.features && (
                    <div className={`flex flex-wrap gap-2 ${
                      index % 2 === 0 ? 'md:justify-end' : ''
                    }`}>
                      {milestone.features.map((feature, fi) => (
                        <span key={fi} className="text-xs bg-dark text-gray-400 px-2 py-1 rounded">
                          {feature}
                        </span>
                      ))}
                    </div>
                  )}
                </div>
              </div>

              {/* Spacer for alternating layout */}
              <div className="hidden md:block md:w-1/2" />
            </div>
          ))}
        </div>
      </div>

      {/* Tech Stack */}
      <div className="max-w-4xl mx-auto mb-16">
        <h2 className="text-2xl font-bold text-center text-white mb-8">
          <span className="bg-gradient-to-r from-primary to-purple-500 bg-clip-text text-transparent">
            Technologies Used
          </span>
        </h2>
        
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {techStack.map((tech, index) => (
            <div 
              key={index}
              className="bg-secondary/50 backdrop-blur rounded-xl p-4 border border-gray-800 
                       hover:border-primary/30 hover:scale-105 transition-all text-center"
            >
              <div className="text-lg font-semibold text-white">{tech.name}</div>
              <div className="text-xs text-primary">{tech.category}</div>
            </div>
          ))}
        </div>
      </div>

      {/* Vision */}
      <div className="max-w-4xl mx-auto">
        <div className="bg-gradient-to-br from-primary/10 to-purple-500/10 rounded-2xl p-8 border border-primary/20 text-center">
          <FaYoutube className="text-5xl text-red-500 mx-auto mb-4" />
          <h2 className="text-2xl font-bold text-white mb-4">The Vision</h2>
          <p className="text-gray-400 max-w-2xl mx-auto mb-6">
            To transform every YouTube video into a complete learning experience. 
            Where watching becomes understanding, and understanding becomes creating. 
            Making education accessible, engaging, and powerful for everyone.
          </p>
          <div className="flex items-center justify-center gap-2 text-primary">
            <FaChartLine />
            <span className="font-semibold">Learning, Evolved.</span>
          </div>
        </div>
      </div>

      {/* Decorative elements */}
      <div className="fixed top-40 left-10 w-72 h-72 bg-primary/5 rounded-full blur-3xl pointer-events-none" />
      <div className="fixed bottom-20 right-10 w-80 h-80 bg-purple-500/5 rounded-full blur-3xl pointer-events-none" />
    </div>
  )
}
