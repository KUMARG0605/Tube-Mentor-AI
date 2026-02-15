export default function LoadingSpinner({ text = 'Loading...' }) {
  return (
    <div className="flex flex-col items-center justify-center py-12">
      <div className="w-10 h-10 border-3 border-primary border-t-transparent rounded-full animate-spin mb-3" />
      <p className="text-gray-400 text-sm">{text}</p>
    </div>
  )
}
