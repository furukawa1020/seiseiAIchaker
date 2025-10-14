'use client'

import { useEffect, useState } from 'react'
import Link from 'next/link'
import { BookOpen, ExternalLink, CheckCircle, AlertTriangle, XCircle } from 'lucide-react'
import { workApi, Work } from '@/lib/api'
import { truncate } from '@/lib/utils'

interface WorksListProps {
  showAll?: boolean
}

export function WorksList({ showAll = false }: WorksListProps) {
  const [works, setWorks] = useState<Work[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadWorks()
  }, [showAll])

  const loadWorks = async () => {
    try {
      setLoading(true)
      const data = await workApi.getWorks(showAll ? undefined : 10)
      setWorks(data)
    } catch (error) {
      console.error('Failed to load works:', error)
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <div className="card">
        <div className="flex items-center justify-center py-12">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
        </div>
      </div>
    )
  }

  if (works.length === 0) {
    return (
      <div className="card">
        <div className="text-center py-12">
          <BookOpen className="w-16 h-16 text-gray-400 mx-auto mb-4" />
          <p className="text-gray-600 text-lg">
            文献が登録されていません
          </p>
          <p className="text-gray-500 text-sm mt-2">
            上のフォームからCSL-JSONファイルをインポートしてください
          </p>
        </div>
      </div>
    )
  }

  return (
    <div className="card">
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-2">
          <BookOpen className="w-6 h-6 text-blue-600" />
          <h2 className="text-2xl font-bold text-gray-900">
            {showAll ? '全文献' : '最近の文献'}
          </h2>
          <span className="badge badge-info">{works.length}件</span>
        </div>
        
        {!showAll && works.length >= 10 && (
          <Link href="/works" className="text-blue-600 hover:text-blue-700 text-sm font-medium">
            すべて表示 →
          </Link>
        )}
      </div>

      <div className="overflow-x-auto">
        <table className="w-full">
          <thead>
            <tr className="border-b border-gray-200">
              <th className="text-left py-3 px-4 font-semibold text-gray-700">タイトル</th>
              <th className="text-left py-3 px-4 font-semibold text-gray-700">著者</th>
              <th className="text-center py-3 px-4 font-semibold text-gray-700">年</th>
              <th className="text-center py-3 px-4 font-semibold text-gray-700">状態</th>
              <th className="text-center py-3 px-4 font-semibold text-gray-700">詳細</th>
            </tr>
          </thead>
          <tbody>
            {works.map((work) => (
              <tr key={work.id} className="border-b border-gray-100 hover:bg-gray-50 transition-colors">
                <td className="py-4 px-4">
                  <div className="flex items-start gap-2">
                    <div className="flex-1">
                      <p className="font-medium text-gray-900 mb-1">
                        {truncate(work.title, 80)}
                      </p>
                      <div className="flex flex-wrap gap-1">
                        {work.peer_reviewed === 1 && (
                          <span className="badge badge-success text-xs">査読あり</span>
                        )}
                        {work.retracted && (
                          <span className="badge badge-danger text-xs">撤回</span>
                        )}
                        {work.doi && (
                          <span className="badge badge-info text-xs">DOI</span>
                        )}
                      </div>
                    </div>
                  </div>
                </td>
                <td className="py-4 px-4">
                  <p className="text-sm text-gray-600">
                    {work.authors && work.authors.length > 0
                      ? truncate(
                          work.authors.map(a => a.family).join(', '),
                          30
                        )
                      : '—'}
                  </p>
                </td>
                <td className="py-4 px-4 text-center">
                  <span className="text-sm text-gray-700">
                    {work.issued_year || '—'}
                  </span>
                </td>
                <td className="py-4 px-4 text-center">
                  {work.retracted ? (
                    <XCircle className="w-5 h-5 text-red-500 mx-auto" />
                  ) : work.peer_reviewed === 1 ? (
                    <CheckCircle className="w-5 h-5 text-green-500 mx-auto" />
                  ) : (
                    <AlertTriangle className="w-5 h-5 text-yellow-500 mx-auto" />
                  )}
                </td>
                <td className="py-4 px-4 text-center">
                  <Link
                    href={`/works/${work.id}`}
                    className="inline-flex items-center gap-1 text-blue-600 hover:text-blue-700 text-sm font-medium"
                  >
                    <ExternalLink className="w-4 h-4" />
                    詳細
                  </Link>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
