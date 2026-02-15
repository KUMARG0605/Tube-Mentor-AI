import { useNavigate } from 'react-router-dom'
import { FaPlay, FaUser, FaCalendar } from 'react-icons/fa'

export default function VideoCard({ video }) {
  const navigate = useNavigate()

  return (
    <div
      onClick={() => navigate(`/video/${video.video_id}`)}
      className="group bg-dark border border-gray-800 rounded-xl overflow-hidden 
                 cursor-pointer hover:border-primary/50 hover:shadow-lg hover:shadow-primary/10 
                 transition-all duration-300"
    >
      {/* Thumbnail */}
      <div className="relative aspect-video overflow-hidden">
        <img
          src={video.thumbnail_url}
          alt={video.title}
          className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
        />
        <div className="absolute inset-0 bg-black/0 group-hover:bg-black/30 transition-colors 
                        flex items-center justify-center">
          <FaPlay className="text-white text-3xl opacity-0 group-hover:opacity-100 transition-opacity" />
        </div>
      </div>

      {/* Info */}
      <div className="p-4">
        <h3 className="font-semibold text-sm text-white line-clamp-2 group-hover:text-primary transition-colors">
          {video.title}
        </h3>
        <div className="flex items-center gap-3 mt-2 text-xs text-gray-500">
          <span className="flex items-center gap-1">
            <FaUser className="text-primary/60" />
            {video.channel_name}
          </span>
          <span className="flex items-center gap-1">
            <FaCalendar className="text-primary/60" />
            {new Date(video.published_at).toLocaleDateString()}
          </span>
        </div>
        <p className="text-xs text-gray-600 mt-2 line-clamp-2">{video.description}</p>
      </div>
    </div>
  )
}
