import { Github, Heart } from 'lucide-react'

export function Footer() {
  return (
    <footer className="bg-gray-900 text-gray-300 mt-16">
      <div className="container mx-auto px-4 py-8 max-w-7xl">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          <div>
            <h3 className="text-white font-bold text-lg mb-4">RefSys</h3>
            <p className="text-sm leading-relaxed">
              正確な参考文献管理と引用支援のための<br />
              無料・ローカル優先のオープンソースシステム
            </p>
          </div>

          <div>
            <h3 className="text-white font-bold text-lg mb-4">機能</h3>
            <ul className="space-y-2 text-sm">
              <li>• CSL-JSON形式インポート</li>
              <li>• DOI/URL実在性検証</li>
              <li>• PDF既読証跡管理</li>
              <li>• APA/IEEE自動整形</li>
              <li>• 査読・撤回チェック</li>
            </ul>
          </div>

          <div>
            <h3 className="text-white font-bold text-lg mb-4">ライセンス</h3>
            <p className="text-sm mb-4">
              MIT License<br />
              著作権配慮・API利用規約準拠
            </p>
            <a 
              href="https://github.com/furukawa1020/seiseiAIchaker"
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center gap-2 text-sm hover:text-white transition-colors"
            >
              <Github className="w-4 h-4" />
              GitHub
            </a>
          </div>
        </div>

        <div className="border-t border-gray-800 mt-8 pt-6 text-center text-sm">
          <p className="flex items-center justify-center gap-2">
            Made with <Heart className="w-4 h-4 text-red-500" /> for researchers
          </p>
          <p className="text-gray-500 mt-2">
            © 2025 RefSys. All rights reserved.
          </p>
        </div>
      </div>
    </footer>
  )
}
