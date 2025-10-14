'use client'

import { useState } from 'react'
import { FileText, Copy, Check } from 'lucide-react'
import { workApi } from '@/lib/api'

interface CitationGeneratorProps {
  workId: string
}

export function CitationGenerator({ workId }: CitationGeneratorProps) {
  const [format, setFormat] = useState('apa')
  const [citation, setCitation] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)
  const [copied, setCopied] = useState(false)

  const handleGenerate = async () => {
    try {
      setLoading(true)
      const result = await workApi.getCitation(workId, format)
      setCitation(result)
    } catch (error) {
      console.error('Failed to generate citation:', error)
      alert('引用生成に失敗しました')
    } finally {
      setLoading(false)
    }
  }

  const handleCopy = () => {
    if (citation) {
      navigator.clipboard.writeText(citation)
      setCopied(true)
      setTimeout(() => setCopied(false), 2000)
    }
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center gap-3">
        <select
          value={format}
          onChange={(e) => setFormat(e.target.value)}
          className="input max-w-xs"
        >
          <option value="apa">APA 7th</option>
          <option value="ieee">IEEE</option>
          <option value="bibtex">BibTeX</option>
        </select>

        <button
          onClick={handleGenerate}
          disabled={loading}
          className="btn btn-secondary"
        >
          {loading ? '生成中...' : '📝 引用を生成'}
        </button>
      </div>

      {citation && (
        <div className="border border-gray-200 rounded-lg p-4 bg-gray-50">
          <div className="flex items-start justify-between gap-3 mb-3">
            <div className="flex items-center gap-2">
              <FileText className="w-5 h-5 text-gray-600" />
              <span className="text-sm font-medium text-gray-700">
                {format.toUpperCase()} 形式
              </span>
            </div>
            <button
              onClick={handleCopy}
              className="flex items-center gap-2 text-sm text-blue-600 hover:text-blue-700 font-medium"
            >
              {copied ? (
                <>
                  <Check className="w-4 h-4" />
                  コピー済み
                </>
              ) : (
                <>
                  <Copy className="w-4 h-4" />
                  コピー
                </>
              )}
            </button>
          </div>
          
          <pre className="text-sm text-gray-800 whitespace-pre-wrap font-mono leading-relaxed">
            {citation}
          </pre>
        </div>
      )}
    </div>
  )
}
