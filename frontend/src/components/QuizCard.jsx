import { useState } from 'react'
import { FaCheckCircle, FaTimesCircle } from 'react-icons/fa'

// Interactive quiz component with answer reveal and scoring
export default function QuizCard({ questions }) {
  const [selected, setSelected] = useState({})   // User selections by question index
  const [revealed, setRevealed] = useState({})   // Revealed answers by question index

  const handleSelect = (qIdx, option) => {
    if (revealed[qIdx]) return
    setSelected((prev) => ({ ...prev, [qIdx]: option }))
  }

  const handleReveal = (qIdx) => {
    setRevealed((prev) => ({ ...prev, [qIdx]: true }))
  }

  const score = Object.keys(revealed).reduce((acc, qIdx) => {
    if (selected[qIdx] === questions[qIdx]?.correct_answer) return acc + 1
    return acc
  }, 0)

  return (
    <div className="space-y-6">
      {Object.keys(revealed).length > 0 && (
        <div className="bg-dark rounded-lg px-4 py-2 text-sm text-center">
          Score: <span className="text-primary font-bold">{score}</span> / {Object.keys(revealed).length}
        </div>
      )}

      {questions.map((q, qIdx) => (
        <div key={qIdx} className="bg-dark border border-gray-800 rounded-xl p-5">
          <p className="font-semibold text-white mb-3">
            <span className="text-primary mr-2">Q{qIdx + 1}.</span>
            {q.question}
          </p>

          <div className="space-y-2">
            {q.options.map((opt, oIdx) => {
              const isSelected = selected[qIdx] === opt
              const isCorrect = revealed[qIdx] && opt === q.correct_answer
              const isWrong = revealed[qIdx] && isSelected && opt !== q.correct_answer

              return (
                <button
                  key={oIdx}
                  onClick={() => handleSelect(qIdx, opt)}
                  className={`w-full text-left px-4 py-2.5 rounded-lg text-sm transition-all 
                    ${isCorrect ? 'bg-green-900/40 border-green-500 text-green-300' : ''}
                    ${isWrong ? 'bg-red-900/40 border-red-500 text-red-300' : ''}
                    ${!revealed[qIdx] && isSelected ? 'bg-primary/20 border-primary text-primary' : ''}
                    ${!revealed[qIdx] && !isSelected ? 'bg-secondary border-gray-700 hover:border-gray-500 text-gray-300' : ''}
                    border`}
                >
                  <span className="flex items-center justify-between">
                    {opt}
                    {isCorrect && <FaCheckCircle className="text-green-400" />}
                    {isWrong && <FaTimesCircle className="text-red-400" />}
                  </span>
                </button>
              )
            })}
          </div>

          {selected[qIdx] && !revealed[qIdx] && (
            <button
              onClick={() => handleReveal(qIdx)}
              className="mt-3 px-4 py-2 bg-primary/20 text-primary text-xs rounded-lg hover:bg-primary/30 transition-colors"
            >
              Check Answer
            </button>
          )}

          {revealed[qIdx] && q.explanation && (
            <div className="mt-3 px-4 py-2 bg-accent/20 rounded-lg text-xs text-gray-300">
              <span className="text-primary font-semibold">Explanation: </span>
              {q.explanation}
            </div>
          )}
        </div>
      ))}
    </div>
  )
}
