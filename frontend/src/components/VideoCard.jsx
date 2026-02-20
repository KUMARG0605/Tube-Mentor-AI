import { useNavigate } from 'react-router-dom'
import { FaPlay, FaUser, FaCalendar, FaClock } from 'react-icons/fa'

export default function VideoCard({ video }) {
  const navigate = useNavigate()

  return (
    <div
      onClick={() => navigate(`/video/${video.video_id}`)}
      className="group bg-secondary/50 backdrop-blur border border-gray-800 rounded-2xl overflow-hidden 
                 cursor-pointer hover:border-cyan-500/30 hover:shadow-xl hover:shadow-cyan-500/10 
                 hover:scale-[1.02] active:scale-[0.98] transition-all duration-300"
    >
      {/* Thumbnail */}
      <div className="relative aspect-video overflow-hidden">
        <img
          src={video.thumbnail_url}
          alt={video.title}
          className="w-full h-full object-cover group-hover:scale-110 transition-transform duration-500"
        />
        <div className="absolute inset-0 bg-gradient-to-t from-dark/80 via-transparent to-transparent" />
        <div className="absolute inset-0 bg-cyan-500/0 group-hover:bg-cyan-500/10 transition-colors 
                        flex items-center justify-center">
          <div className="w-14 h-14 rounded-full bg-gradient-to-br from-cyan-500 to-purple-500 
                         flex items-center justify-center opacity-0 group-hover:opacity-100 
                         scale-50 group-hover:scale-100 transition-all duration-300 shadow-lg">
            <FaPlay className="text-white text-lg ml-1" />
          </div>
        </div>
        {video.duration && (
          <span className="absolute bottom-2 right-2 bg-black/80 text-white text-xs px-2 py-1 rounded-md flex items-center gap-1">
            <FaClock className="text-[10px]" />
            {video.duration}
          </span>
        )}
      </div>

      {/* Info */}
      <div className="p-4">
        <h3 className="font-semibold text-sm text-white line-clamp-2 group-hover:text-cyan-400 transition-colors">
          {video.title}
        </h3>
        <div className="flex items-center gap-3 mt-3 text-xs text-gray-500">
          <span className="flex items-center gap-1.5 bg-dark/50 px-2 py-1 rounded-lg">
            <FaUser className="text-cyan-400/60" />
            <span className="truncate max-w-[120px]">{video.channel_name}</span>
          </span>
          <span className="flex items-center gap-1">
            <FaCalendar className="text-purple-400/60" />
            {new Date(video.published_at).toLocaleDateString()}
          </span>
        </div>
        <p className="text-xs text-gray-600 mt-3 line-clamp-2">{video.description}</p>
      </div>
    </div>
  )
}
