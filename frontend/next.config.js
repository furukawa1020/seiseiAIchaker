/** @type {import('next').NextConfig} */
const nextConfig = {
  // 開発環境のみrewritesを有効化（本番環境では環境変数を使用）
  async rewrites() {
    // 本番環境では環境変数NEXT_PUBLIC_API_URLを使うのでrewritesは不要
    if (process.env.NODE_ENV === 'production') {
      return []
    }
    return [
      {
        source: '/api/:path*',
        destination: 'http://localhost:8000/:path*',
      },
    ]
  },
  // Webpack設定でパスエイリアスを明示的に解決
  webpack: (config) => {
    const path = require('path')
    config.resolve.alias['@'] = path.resolve(__dirname, 'src')
    return config
  },
}

module.exports = nextConfig
