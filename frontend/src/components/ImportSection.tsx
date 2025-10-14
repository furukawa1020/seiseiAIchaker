'use client'

import { useState } from 'react'
import { useDropzone } from 'react-dropzone'
import { Upload, FileJson, FileText, AlertCircle } from 'lucide-react'
import { workApi } from '@/lib/api'

interface ImportSectionProps {
  onImportSuccess?: () => void
}

export function ImportSection({ onImportSuccess }: ImportSectionProps) {
  const [importing, setImporting] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [success, setSuccess] = useState<string | null>(null)
  const [importMode, setImportMode] = useState<'json' | 'pdf'>('pdf')

  const onDrop = async (acceptedFiles: File[]) => {
    if (acceptedFiles.length === 0) return

    const file = acceptedFiles[0]
    setImporting(true)
    setError(null)
    setSuccess(null)

    try {
      if (file.name.endsWith('.pdf')) {
        // PDFアップロード
        const result = await workApi.uploadPdf(file)
        setSuccess(`✓ PDFから文献情報を抽出しました: ${result.title}`)
      } else {
        // JSON インポート
        const text = await file.text()
        const json = JSON.parse(text)
        const result = await workApi.importWorks(json)
        setSuccess(`✓ ${result.imported || 0}件の文献をインポートしました`)
      }
      
      onImportSuccess?.()
    } catch (err: any) {
      setError(err.message || 'インポートに失敗しました')
    } finally {
      setImporting(false)
    }
  }

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: importMode === 'pdf' 
      ? { 'application/pdf': ['.pdf'] }
      : { 'application/json': ['.json'] },
    multiple: false,
  })

  return (
    <div className="card">
      <div className="flex items-center gap-2 mb-4">
        <Upload className="w-6 h-6 text-blue-600" />
        <h2 className="text-2xl font-bold text-gray-900">文献をインポート</h2>
      </div>

      {/* モード切り替えタブ */}
      <div className="flex gap-2 mb-4">
        <button
          onClick={() => setImportMode('pdf')}
          className={`flex-1 px-4 py-2 rounded-lg font-medium transition-colors ${
            importMode === 'pdf'
              ? 'bg-blue-600 text-white'
              : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
          }`}
        >
          <FileText className="w-4 h-4 inline mr-2" />
          PDF アップロード
        </button>
        <button
          onClick={() => setImportMode('json')}
          className={`flex-1 px-4 py-2 rounded-lg font-medium transition-colors ${
            importMode === 'json'
              ? 'bg-blue-600 text-white'
              : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
          }`}
        >
          <FileJson className="w-4 h-4 inline mr-2" />
          JSON インポート
        </button>
      </div>

      <div
        {...getRootProps()}
        className={`
          border-2 border-dashed rounded-xl p-12 text-center cursor-pointer
          transition-all duration-200
          ${isDragActive 
            ? 'border-blue-500 bg-blue-50' 
            : 'border-gray-300 hover:border-blue-400 hover:bg-gray-50'
          }
          ${importing ? 'opacity-50 cursor-not-allowed' : ''}
        `}
      >
        <input {...getInputProps()} disabled={importing} />
        
        <Upload className={`w-16 h-16 mx-auto mb-4 ${
          isDragActive ? 'text-blue-500' : 'text-gray-400'
        }`} />
        
        {importing ? (
          <p className="text-lg text-gray-600">
            {importMode === 'pdf' ? 'PDF処理中...' : 'インポート中...'}
          </p>
        ) : isDragActive ? (
          <p className="text-lg text-blue-600 font-medium">
            ここにドロップしてください
          </p>
        ) : (
          <>
            <p className="text-lg text-gray-700 mb-2">
              {importMode === 'pdf' 
                ? '📄 PDFファイルをドラッグ＆ドロップ'
                : 'CSL-JSON ファイルをドラッグ＆ドロップ'
              }
            </p>
            <p className="text-sm text-gray-500">
              または、クリックしてファイルを選択
            </p>
            {importMode === 'pdf' && (
              <p className="text-xs text-gray-400 mt-2">
                💡 PDFからタイトル・著者・発行年を自動抽出します
              </p>
            )}
          </>
        )}
      </div>

      {error && (
        <div className="mt-4 p-4 bg-red-50 border border-red-200 rounded-lg flex items-start gap-3">
          <AlertCircle className="w-5 h-5 text-red-600 flex-shrink-0 mt-0.5" />
          <div className="flex-1">
            <p className="text-red-800 font-medium">エラー</p>
            <p className="text-red-700 text-sm">{error}</p>
          </div>
        </div>
      )}

      {success && (
        <div className="mt-4 p-4 bg-green-50 border border-green-200 rounded-lg">
          <p className="text-green-800">{success}</p>
        </div>
      )}

      <div className="mt-6 p-4 bg-blue-50 rounded-lg">
        <p className="text-sm text-blue-900 font-medium mb-2">
          💡 ヒント: CSL-JSON形式について
        </p>
        <ul className="text-sm text-blue-800 space-y-1">
          <li>• Zotero: 選択 → 右クリック → "エクスポート" → "CSL JSON"</li>
          <li>• Mendeley: File → Export → CSL JSON</li>
          <li>• 手動: <code className="bg-white px-1 rounded">examples/sample_works.json</code> を参考</li>
        </ul>
      </div>
    </div>
  )
}
