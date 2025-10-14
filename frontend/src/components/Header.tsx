import Link from 'next/link'
import { BookOpen } from 'lucide-react'

export function Header() {
  return (
    <header className="bg-white border-b border-gray-200 sticky top-0 z-50 shadow-sm">
      <div className="container mx-auto px-4 py-4 max-w-7xl">
        <div className="flex items-center justify-between">
          <Link href="/" className="flex items-center gap-3 hover:opacity-80 transition-opacity">
            <BookOpen className="w-8 h-8 text-blue-600" />
            <div>
              <h1 className="text-2xl font-bold text-gray-900">RefSys</h1>
              <p className="text-xs text-gray-600">参考文献管理システム</p>
            </div>
          </Link>

          <nav className="flex items-center gap-6">
            <Link 
              href="/" 
              className="text-gray-700 hover:text-blue-600 font-medium transition-colors"
            >
              ホーム
            </Link>
            <Link 
              href="/works" 
              className="text-gray-700 hover:text-blue-600 font-medium transition-colors"
            >
              文献リスト
            </Link>
          </nav>
        </div>
      </div>
    </header>
  )
}
