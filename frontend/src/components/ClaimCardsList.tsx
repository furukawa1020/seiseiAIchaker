import { BookMarked, Calendar } from 'lucide-react'
import { ClaimCard } from '@/lib/api'
import { formatDate } from '@/lib/utils'

interface ClaimCardsListProps {
  cards: ClaimCard[]
}

export function ClaimCardsList({ cards }: ClaimCardsListProps) {
  if (cards.length === 0) {
    return (
      <div className="text-center py-8 text-gray-500">
        まだカードが作成されていません
      </div>
    )
  }

  return (
    <div className="space-y-4">
      {cards.map((card) => (
        <div key={card.id} className="border border-gray-200 rounded-lg p-5 hover:shadow-md transition-shadow bg-white">
          <div className="flex items-start gap-3">
            <BookMarked className="w-5 h-5 text-blue-600 flex-shrink-0 mt-1" />
            
            <div className="flex-1 min-w-0">
              <div className="flex items-center gap-2 mb-3">
                {card.page_numbers && (
                  <span className="badge badge-info text-xs">
                    p.{card.page_numbers}
                  </span>
                )}
                <span className="text-xs text-gray-500 flex items-center gap-1">
                  <Calendar className="w-3 h-3" />
                  {formatDate(card.created_at)}
                </span>
              </div>

              <div className="space-y-3">
                <div>
                  <p className="text-xs text-gray-500 font-medium mb-1">主張・引用</p>
                  <p className="text-gray-900 leading-relaxed">
                    {card.claim_text}
                  </p>
                </div>

                <div>
                  <p className="text-xs text-gray-500 font-medium mb-1">文脈・コメント</p>
                  <p className="text-gray-700 text-sm leading-relaxed">
                    {card.context}
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>
      ))}
    </div>
  )
}
