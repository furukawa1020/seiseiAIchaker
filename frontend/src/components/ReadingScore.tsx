'use client'

import { useEffect, useState } from 'react'
import { BookOpen, TrendingUp } from 'lucide-react'
import { workApi } from '@/lib/api'

interface ReadingScoreProps {
  workId: string
}

export function ReadingScore({ workId }: ReadingScoreProps) {
  const [score, setScore] = useState<any>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadScore()
  }, [workId])

  const loadScore = async () => {
    try {
      setLoading(true)
      const data = await workApi.getReadingScore(workId)
      setScore(data)
    } catch (error) {
      console.error('Failed to load reading score:', error)
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <div className="card">
        <div className="animate-pulse flex items-center gap-4">
          <div className="w-16 h-16 bg-gray-200 rounded-full"></div>
          <div className="flex-1">
            <div className="h-4 bg-gray-200 rounded w-3/4 mb-2"></div>
            <div className="h-3 bg-gray-200 rounded w-1/2"></div>
          </div>
        </div>
      </div>
    )
  }

  if (!score) {
    return null
  }

  const getScoreColor = (value: number) => {
    if (value >= 70) return 'text-green-600'
    if (value >= 40) return 'text-yellow-600'
    return 'text-red-600'
  }

  const getScoreLabel = (value: number) => {
    if (value >= 70) return '高い既読度'
    if (value >= 40) return '中程度の既読度'
    return '低い既読度'
  }

  return (
    <div className="card">
      <div className="flex items-center gap-2 mb-6">
        <BookOpen className="w-6 h-6 text-blue-600" />
        <h2 className="text-2xl font-bold text-gray-900">既読スコア</h2>
      </div>

      <div className="flex items-center gap-6">
        <div className="flex-shrink-0">
          <div className="relative w-24 h-24">
            <svg className="w-full h-full transform -rotate-90">
              <circle
                cx="48"
                cy="48"
                r="40"
                fill="none"
                stroke="#e5e7eb"
                strokeWidth="8"
              />
              <circle
                cx="48"
                cy="48"
                r="40"
                fill="none"
                stroke="currentColor"
                strokeWidth="8"
                strokeDasharray={`${2 * Math.PI * 40}`}
                strokeDashoffset={`${2 * Math.PI * 40 * (1 - score.score / 100)}`}
                className={getScoreColor(score.score)}
                strokeLinecap="round"
              />
            </svg>
            <div className="absolute inset-0 flex items-center justify-center">
              <span className={`text-2xl font-bold ${getScoreColor(score.score)}`}>
                {score.score}
              </span>
            </div>
          </div>
        </div>

        <div className="flex-1">
          <p className={`text-lg font-semibold mb-2 ${getScoreColor(score.score)}`}>
            {getScoreLabel(score.score)}
          </p>
          
          <div className="space-y-1 text-sm text-gray-600">
            {score.page_coverage !== undefined && (
              <p>📄 ページカバレッジ: {score.page_coverage}%</p>
            )}
            {score.card_count !== undefined && (
              <p>📝 引用カード: {score.card_count}枚</p>
            )}
            {score.evidence_count !== undefined && (
              <p>✓ 証跡記録: {score.evidence_count}件</p>
            )}
          </div>

          {score.score < 70 && (
            <div className="mt-4 p-3 bg-blue-50 rounded-lg">
              <p className="text-sm text-blue-900">
                💡 スコアを上げるには、引用文脈カードを追加してください
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
