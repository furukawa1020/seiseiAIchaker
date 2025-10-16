# デプロイガイド

## 🚀 デプロイ手順

このプロジェクトは以下の構成でデプロイします：
- **フロントエンド**: Vercel (Next.js)
- **バックエンド**: Railway (FastAPI)

両方とも無料枠で利用可能です！

---

## 📦 事前準備

### 1. GitHubにプッシュ
```bash
git add .
git commit -m "Deploy ready"
git push origin main
```

---

## 🎨 フロントエンドのデプロイ (Vercel)

### 手順:
1. **Vercelにアクセス**: https://vercel.com
2. **GitHubでサインイン**
3. **"Import Project"** または既存プロジェクトの **Settings**
4. **リポジトリを選択**: `seiseiAIchaker`
5. **必須設定（Settings → General）**:
   - Framework Preset: `Next.js`
   - **Root Directory**: `frontend` ← **これが最重要！**
   - Build Command: 空白（デフォルトを使用）
   - Output Directory: 空白（デフォルトを使用）
   - Install Command: 空白（デフォルトを使用）
   - Node.js Version: `18.x` (推奨)
6. **環境変数を追加（Settings → Environment Variables）**:
   ```
   NEXT_PUBLIC_API_URL=https://あなたのバックエンドURL.up.railway.app
   ```
   ※まずは空白でもOK、バックエンドデプロイ後に追加
7. **Save** して **Deployments** → **Redeploy**

**重要:** Root Directoryは必ず `frontend` に設定してください。空白だとエラーになります。

### デプロイ後:
- 自動で `https://あなたのプロジェクト名.vercel.app` にデプロイされます
- GitHubにpushするたびに自動デプロイ！

---

## ⚙️ バックエンドのデプロイ (Railway)

### 手順:
1. **Railwayにアクセス**: https://railway.app
2. **GitHubでサインイン**
3. **"New Project"** をクリック
4. **"Deploy from GitHub repo"** を選択
5. **リポジトリを選択**: `seiseiAIchaker`
6. **自動で検出されるので、そのままデプロイ**
7. **Settings** → **Networking** で公開URLを有効化
8. **Generate Domain** をクリック

### デプロイ後:
- `https://あなたのプロジェクト名.up.railway.app` のようなURLが発行されます
- このURLをコピーして、Vercelの環境変数 `NEXT_PUBLIC_API_URL` に設定
- Vercelで **Redeploy** を実行

### 無料枠について:
- **$5分/月**の無料クレジット
- スリープなし・常時起動
- クレジットカード登録で$5追加（合計$10/月）
- 小規模プロジェクトなら十分！

---

## 🔄 CORS設定の更新

バックエンド (`refsys/ui/app.py`) のCORS設定を更新:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "https://あなたのプロジェクト名.vercel.app",  # Vercelのドメインを追加
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

更新後、GitHubにpushすれば自動的に再デプロイされます！

---

## ✅ デプロイ完了チェックリスト

- [ ] GitHubにコードをプッシュ
- [ ] Railwayでバックエンドをデプロイ
- [ ] バックエンドのURLを取得
- [ ] Vercelでフロントエンドをデプロイ
- [ ] Vercelの環境変数に `NEXT_PUBLIC_API_URL` を設定
- [ ] バックエンドのCORS設定にVercelのドメインを追加
- [ ] 動作確認

---

## 📝 注意事項

### Railwayの無料プラン:
- **$5分/月の無料クレジット**
- スリープなし・常時起動
- 使用量に応じて課金（従量制）
- クレジットカード登録で追加$5/月

### Vercelの無料プラン:
- 商用利用も可能
- 自動HTTPS
- カスタムドメイン設定可能

---

## 🎉 デプロイ成功後

アクセス:
```
https://あなたのプロジェクト名.vercel.app
```

PDF直接アップロード、文献管理、引用生成など、すべての機能が使えます！

---

## トラブルシューティング

### バックエンドが起動しない:
- Railwayのログを確認
- `requirements.txt` に必要なパッケージがすべて含まれているか確認
- Python バージョンが一致しているか確認

### フロントエンドがAPIにアクセスできない:
- `NEXT_PUBLIC_API_URL` が正しく設定されているか確認
- バックエンドのCORS設定にVercelドメインが含まれているか確認
- ブラウザのコンソールでエラーを確認

### データベースがリセットされる:
- Railwayの無料プランはファイルシステムが一時的です
- 永続的なデータベースが必要な場合は、PostgreSQLなどの外部DBを検討

---

## 🆘 サポート

問題が発生した場合は、以下を確認してください:
1. Railwayのデプロイログ
2. Vercelのビルドログ
3. ブラウザの開発者コンソール
4. GitHubのActions（設定している場合）
