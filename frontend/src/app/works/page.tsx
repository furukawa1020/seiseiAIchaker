'use client'

import { WorksList } from '@/components/WorksList'
import { ArrowLeft } from 'lucide-react'
import Link from 'next/link'

export default function WorksPage() {
  return (
    <div className="container mx-auto px-4 py-8 max-w-7xl">
      <div className="mb-6">
        <Link href="/" className="inline-flex items-center gap-2 text-blue-600 hover:text-blue-700">
          <ArrowLeft className="w-4 h-4" />
          ホームに戻る
        </Link>
      </div>

      <div className="card mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-4">📚 文献リスト</h1>
        <p className="text-gray-600">
          登録されているすべての文献を管理・確認できます。
        </p>
      </div>

      <WorksList showAll />
    </div>
  )
}
