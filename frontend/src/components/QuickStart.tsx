import { Zap, BookOpen, CheckCircle, FileText } from 'lucide-react'

export function QuickStart() {
  return (
    <div className="card">
      <div className="flex items-center gap-2 mb-6">
        <Zap className="w-6 h-6 text-yellow-500" />
        <h2 className="text-2xl font-bold text-gray-900">クイックスタート</h2>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="space-y-3">
          <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center">
            <BookOpen className="w-6 h-6 text-blue-600" />
          </div>
          <h3 className="font-bold text-lg text-gray-900">1. インポート</h3>
          <p className="text-sm text-gray-600 leading-relaxed">
            Zotero/MendeleyからCSL-JSON形式でエクスポートした文献データをドラッグ&ドロップでインポート
          </p>
        </div>

        <div className="space-y-3">
          <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center">
            <CheckCircle className="w-6 h-6 text-green-600" />
          </div>
          <h3 className="font-bold text-lg text-gray-900">2. 検証</h3>
          <p className="text-sm text-gray-600 leading-relaxed">
            DOI/URLの実在性を自動検証。査読状況、撤回チェック、引用数の確認も可能
          </p>
        </div>

        <div className="space-y-3">
          <div className="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center">
            <FileText className="w-6 h-6 text-purple-600" />
          </div>
          <h3 className="font-bold text-lg text-gray-900">3. 引用生成</h3>
          <p className="text-sm text-gray-600 leading-relaxed">
            APA 7th / IEEE形式で正確な参考文献リストを自動生成。コピー&ペーストですぐに使用可能
          </p>
        </div>
      </div>

      <div className="mt-8 p-4 bg-gradient-to-r from-blue-50 to-purple-50 rounded-lg border border-blue-200">
        <p className="text-sm font-medium text-gray-900 mb-2">
          💡 Pro Tip: 既読証跡を残そう
        </p>
        <p className="text-sm text-gray-700">
          文献詳細ページから「引用文脈カード」を作成することで、どの主張をどのページから引用したかを記録できます。
          これにより既読スコアが向上し、後から論文を書く際に役立ちます。
        </p>
      </div>
    </div>
  )
}
