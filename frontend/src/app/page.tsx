'use client'

import { useState } from 'react'
import { ImportSection } from '@/components/ImportSection'
import { WorksList } from '@/components/WorksList'
import { QuickStart } from '@/components/QuickStart'
import { BookOpen, CheckCircle, FileText, Search, Upload } from 'lucide-react'

export default function Home() {
  const [refreshTrigger, setRefreshTrigger] = useState(0)

  const handleImportSuccess = () => {
    setRefreshTrigger(prev => prev + 1)
  }

  return (
    <div className="container mx-auto px-4 py-8 max-w-7xl">
      {/* Hero Section */}
      <div className="text-center mb-12">
        <h1 className="text-4xl font-bold text-gray-900 mb-4">
          📚 RefSys
        </h1>
        <p className="text-xl text-gray-600 mb-6">
          正確な参考文献・引用テンプレ自動生成＋実在性/既読検証システム
        </p>
        <div className="flex flex-wrap justify-center gap-4 text-sm text-gray-600">
          <div className="flex items-center gap-2">
            <CheckCircle className="w-4 h-4 text-green-600" />
            <span>実在性検証</span>
          </div>
          <div className="flex items-center gap-2">
            <BookOpen className="w-4 h-4 text-blue-600" />
            <span>既読証跡</span>
          </div>
          <div className="flex items-center gap-2">
            <FileText className="w-4 h-4 text-purple-600" />
            <span>APA/IEEE対応</span>
          </div>
          <div className="flex items-center gap-2">
            <Search className="w-4 h-4 text-orange-600" />
            <span>無料・ローカル優先</span>
          </div>
        </div>
      </div>

      {/* Import Section */}
      <div className="mb-8">
        <ImportSection onImportSuccess={handleImportSuccess} />
      </div>

      {/* Works List */}
      <div className="mb-8">
        <WorksList key={refreshTrigger} />
      </div>

      {/* Quick Start */}
      <div>
        <QuickStart />
      </div>
    </div>
  )
}
