'use client'

import { useEffect, useState } from 'react'
import { useParams } from 'next/navigation'
import Link from 'next/link'
import { ArrowLeft, CheckCircle, AlertTriangle, XCircle, FileText, BookMarked } from 'lucide-react'
import { workApi } from '@/lib/api'
import { VerificationResults } from '@/components/VerificationResults'
import { ClaimCardForm } from '@/components/ClaimCardForm'
import { ClaimCardsList } from '@/components/ClaimCardsList'
import { ReadingScore } from '@/components/ReadingScore'
import { CitationGenerator } from '@/components/CitationGenerator'

export default function WorkDetailPage() {
  const params = useParams()
  const workId = params.id as string

  const [work, setWork] = useState<any>(null)
  const [checks, setChecks] = useState<any[]>([])
  const [cards, setCards] = useState<any[]>([])
  const [loading, setLoading] = useState(true)
  const [verifying, setVerifying] = useState(false)

  useEffect(() => {
    loadWorkDetail()
  }, [workId])

  const loadWorkDetail = async () => {
    try {
      setLoading(true)
      const [workData, checksData, cardsData] = await Promise.all([
        workApi.getWork(workId),
        workApi.getChecks(workId),
        workApi.getCards(workId),
      ])
      setWork(workData)
      setChecks(checksData)
      setCards(cardsData)
    } catch (error) {
      console.error('Failed to load work detail:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleVerify = async () => {
    try {
      setVerifying(true)
      await workApi.verifyWork(workId)
      await loadWorkDetail()
    } catch (error) {
      console.error('Verification failed:', error)
      alert('検証に失敗しました')
    } finally {
      setVerifying(false)
    }
  }

  const handleCardCreated = () => {
    loadWorkDetail()
  }

  if (loading) {
    return (
      <div className="container mx-auto px-4 py-8 max-w-7xl">
        <div className="flex items-center justify-center h-64">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
        </div>
      </div>
    )
  }

  if (!work) {
    return (
      <div className="container mx-auto px-4 py-8 max-w-7xl">
        <div className="card">
          <p className="text-center text-gray-600">文献が見つかりませんでした</p>
        </div>
      </div>
    )
  }

  return (
    <div className="container mx-auto px-4 py-8 max-w-7xl">
      {/* Navigation */}
      <div className="mb-6">
        <Link href="/works" className="inline-flex items-center gap-2 text-blue-600 hover:text-blue-700">
          <ArrowLeft className="w-4 h-4" />
          文献リストに戻る
        </Link>
      </div>

      {/* Work Details */}
      <div className="card mb-6">
        <h1 className="text-3xl font-bold text-gray-900 mb-4">{work.title}</h1>
        
        <div className="space-y-2 text-gray-700 mb-6">
          <p><strong>タイプ:</strong> {work.type}</p>
          
          {work.authors && work.authors.length > 0 && (
            <p>
              <strong>著者:</strong>{' '}
              {work.authors.map((a: any) => `${a.given || ''} ${a.family || ''}`.trim()).join(', ')}
            </p>
          )}
          
          {work.issued_year && (
            <p><strong>発行年:</strong> {work.issued_year}</p>
          )}
          
          {work.container_title && (
            <p><strong>掲載誌:</strong> {work.container_title}</p>
          )}
          
          {work.doi && (
            <p>
              <strong>DOI:</strong>{' '}
              <a 
                href={`https://doi.org/${work.doi}`} 
                target="_blank" 
                rel="noopener noreferrer"
                className="text-blue-600 hover:underline"
              >
                {work.doi}
              </a>
            </p>
          )}
          
          {work.url && (
            <p>
              <strong>URL:</strong>{' '}
              <a 
                href={work.url} 
                target="_blank" 
                rel="noopener noreferrer"
                className="text-blue-600 hover:underline break-all"
              >
                {work.url}
              </a>
            </p>
          )}
        </div>

        {/* Badges */}
        <div className="flex flex-wrap gap-2 mb-6">
          {work.peer_reviewed === 1 && (
            <span className="badge badge-success">✓ 査読あり</span>
          )}
          {work.peer_reviewed === 0 && (
            <span className="badge badge-warning">査読なし</span>
          )}
          {work.retracted && (
            <span className="badge badge-danger">⚠ 撤回済み</span>
          )}
          {work.consensus_score !== null && (
            <span className="badge badge-info">
              合意度: {work.consensus_score}/100
            </span>
          )}
        </div>

        {/* Actions */}
        <div className="flex flex-wrap gap-3">
          <button
            onClick={handleVerify}
            disabled={verifying}
            className="btn btn-primary"
          >
            {verifying ? '検証中...' : '🔍 実在性検証を実行'}
          </button>
          <CitationGenerator workId={workId} />
        </div>
      </div>

      {/* Verification Results */}
      {checks.length > 0 && (
        <div className="mb-6">
          <VerificationResults checks={checks} />
        </div>
      )}

      {/* Reading Score */}
      <div className="mb-6">
        <ReadingScore workId={workId} />
      </div>

      {/* Claim Cards */}
      <div className="card mb-6">
        <div className="flex items-center gap-2 mb-6">
          <BookMarked className="w-6 h-6 text-blue-600" />
          <h2 className="text-2xl font-bold text-gray-900">引用文脈カード</h2>
        </div>

        {cards.length > 0 && (
          <div className="mb-6">
            <ClaimCardsList cards={cards} />
          </div>
        )}

        <div>
          <h3 className="text-lg font-semibold text-gray-900 mb-4">新しいカードを作成</h3>
          <ClaimCardForm workId={workId} onSuccess={handleCardCreated} />
        </div>
      </div>
    </div>
  )
}
