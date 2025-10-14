# RefSys - Next.js Frontend Setup Guide

## クイックスタート (PowerShell)

### 1. Node.jsのインストール確認

```powershell
node --version
npm --version
```

Node.js 18以上が必要です。インストールされていない場合:
https://nodejs.org/ からLTS版をダウンロード

### 2. 依存関係のインストール

```powershell
cd frontend
npm install
```

### 3. 環境変数の設定

`.env.local` ファイルを作成:

```powershell
@"
NEXT_PUBLIC_API_URL=http://localhost:8000
"@ | Out-File -FilePath .env.local -Encoding UTF8
```

### 4. バックエンドとフロントエンドを同時起動

**PowerShellスクリプトを使う場合** (推奨):

```powershell
# プロジェクトルートに移動
cd ..

# 起動スクリプトを実行
.\start-dev.ps1
```

**手動で起動する場合**:

ターミナル1 (バックエンド):
```powershell
python -m refsys server
```

ターミナル2 (フロントエンド):
```powershell
cd frontend
npm run dev
```

### 5. ブラウザで開く

http://localhost:3000

## 🎯 開発ワークフロー

### ホットリロード
ファイルを編集すると自動的にブラウザがリロードされます。

### コンポーネント開発
1. `src/components/` に新しいコンポーネントを追加
2. `src/app/` の必要なページでインポート
3. ブラウザで確認

### API連携の追加
1. `src/lib/api.ts` に新しいAPI関数を追加
2. コンポーネントから呼び出し

例:
```typescript
// api.ts
export const workApi = {
  async getNewData(): Promise<any> {
    const { data } = await api.get('/new-endpoint')
    return data
  },
}

// Component.tsx
const data = await workApi.getNewData()
```

## 🐛 トラブルシューティング

### ポート3000が使用中
```powershell
# プロセスを確認
netstat -ano | findstr :3000

# プロセスを終了 (PIDを取得後)
taskkill /PID <PID> /F

# または別のポートを使用
npm run dev -- -p 3001
```

### node_modulesの再インストール
```powershell
Remove-Item -Recurse -Force node_modules
Remove-Item package-lock.json
npm install
```

### キャッシュのクリア
```powershell
Remove-Item -Recurse -Force .next
npm run dev
```

### APIエラー
- バックエンドが起動しているか確認
- `.env.local` のURLが正しいか確認
- CORS設定を確認 (FastAPI側で `allow_origins=["*"]`)

## 📦 本番ビルド

```powershell
# ビルド
npm run build

# ビルドの確認
npm start
```

## 🚀 Vercelへのデプロイ

```powershell
# Vercel CLIのインストール
npm install -g vercel

# ログイン
vercel login

# デプロイ
vercel
```

環境変数の設定:
```
NEXT_PUBLIC_API_URL=https://your-api-domain.com
```

## 💡 便利なコマンド

```powershell
# 型チェック
npx tsc --noEmit

# Lintチェック
npm run lint

# Lintの自動修正
npm run lint -- --fix

# 依存関係の更新確認
npm outdated

# セキュリティ監査
npm audit
```

## 🎨 スタイルのカスタマイズ

### Tailwindのカスタマイズ
`tailwind.config.ts` を編集:

```typescript
theme: {
  extend: {
    colors: {
      primary: {
        // カスタムカラー
      },
    },
  },
}
```

### グローバルスタイル
`src/app/globals.css` を編集

## 📱 レスポンシブ対応

すべてのコンポーネントはTailwindのレスポンシブクラスで対応:
- `md:` - タブレット以上
- `lg:` - デスクトップ以上
- `xl:` - 大画面

## 🔒 セキュリティ

- APIキーは `.env.local` に保存 (Gitにコミットしない)
- `NEXT_PUBLIC_` プレフィックスは公開される
- 機密情報はサーバーサイドで処理

## 📚 参考リンク

- [Next.js Documentation](https://nextjs.org/docs)
- [Tailwind CSS](https://tailwindcss.com/docs)
- [TypeScript Handbook](https://www.typescriptlang.org/docs/)
