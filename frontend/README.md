# RefSys Frontend (Next.js)

RefSysのモダンなフロントエンドアプリケーション。Next.js 14 + TypeScript + Tailwind CSSで構築されています。

## 🚀 セットアップ

### 1. 依存関係のインストール

```bash
cd frontend
npm install
```

### 2. 環境変数の設定

`.env.local`ファイルを作成:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### 3. 開発サーバーの起動

```bash
npm run dev
```

ブラウザで [http://localhost:3000](http://localhost:3000) を開きます。

## 📁 プロジェクト構造

```
frontend/
├── src/
│   ├── app/                 # Next.js App Router
│   │   ├── layout.tsx       # ルートレイアウト
│   │   ├── page.tsx         # ホームページ
│   │   ├── works/           # 文献リストページ
│   │   └── works/[id]/      # 文献詳細ページ
│   ├── components/          # Reactコンポーネント
│   │   ├── Header.tsx       # ヘッダー
│   │   ├── Footer.tsx       # フッター
│   │   ├── ImportSection.tsx      # インポートフォーム
│   │   ├── WorksList.tsx          # 文献リスト
│   │   ├── VerificationResults.tsx # 検証結果表示
│   │   ├── ClaimCardForm.tsx      # カード作成フォーム
│   │   ├── ClaimCardsList.tsx     # カード一覧
│   │   ├── ReadingScore.tsx       # 既読スコア
│   │   ├── CitationGenerator.tsx  # 引用生成
│   │   └── QuickStart.tsx         # クイックスタート
│   └── lib/                 # ユーティリティ
│       ├── api.ts           # APIクライアント
│       └── utils.ts         # ヘルパー関数
├── public/                  # 静的ファイル
├── package.json
├── tsconfig.json
├── tailwind.config.ts
└── next.config.js
```

## 🎨 技術スタック

- **Next.js 14** - React フレームワーク (App Router)
- **TypeScript** - 型安全性
- **Tailwind CSS** - ユーティリティファーストCSS
- **Axios** - HTTP クライアント
- **SWR** - データフェッチング
- **React Hook Form** - フォーム管理
- **React Dropzone** - ファイルドロップ
- **Lucide React** - アイコン

## 🔗 API連携

FastAPIバックエンドと連携します。`next.config.js`でAPIプロキシを設定:

```javascript
async rewrites() {
  return [
    {
      source: '/api/:path*',
      destination: 'http://localhost:8000/:path*',
    },
  ]
}
```

## 📝 主要機能

### ホームページ (`/`)
- CSL-JSONファイルのインポート
- 最近の文献一覧
- クイックスタートガイド

### 文献リスト (`/works`)
- 全文献の一覧表示
- フィルタリング・ソート
- 検証状態の表示

### 文献詳細 (`/works/[id]`)
- 詳細情報表示
- 実在性検証の実行
- 既読スコアの表示
- 引用文脈カードの管理
- 引用テキストの生成

## 🛠️ 開発コマンド

```bash
# 開発サーバー起動
npm run dev

# 本番ビルド
npm run build

# 本番サーバー起動
npm start

# Lintチェック
npm run lint
```

## 🎯 使い方

1. **バックエンドを起動**: まず `refsys` のFastAPIサーバーを起動してください
   ```bash
   cd ..
   python -m refsys server
   ```

2. **フロントエンドを起動**: 別のターミナルで
   ```bash
   cd frontend
   npm run dev
   ```

3. **ブラウザで開く**: http://localhost:3000 にアクセス

4. **文献をインポート**: ZoteroやMendeleyからエクスポートしたCSL-JSONファイルをドラッグ&ドロップ

5. **検証と管理**: 文献詳細ページで実在性検証を実行し、引用カードを作成

## 🌐 本番デプロイ

### Vercelへのデプロイ

```bash
npm install -g vercel
vercel
```

環境変数を設定:
- `NEXT_PUBLIC_API_URL`: バックエンドAPIのURL

### その他のプラットフォーム

- **Netlify**: `npm run build` → `.next` フォルダをデプロイ
- **Docker**: Dockerfileを作成して `docker build`
- **静的エクスポート**: `next export` を使用 (一部機能制限あり)

## 🤝 貢献

バグ報告や機能提案は GitHubの Issues へお願いします。

## 📄 ライセンス

MIT License - 詳細は [LICENSE](../LICENSE) を参照
