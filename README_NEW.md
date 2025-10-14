# RefSys - 正確な参考文献・引用テンプレ自動生成＋実在性/既読検証システム

[![Next.js](https://img.shields.io/badge/Next.js-14-black)](https://nextjs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109-009688)](https://fastapi.tiangolo.com/)
[![License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

## 概要

**RefSys**は、研究者・学生向けの無料・ローカル優先の学術引用管理システムです。

### 主な機能

- **📥 CSL-JSON インポート**: Zotero/Mendeley からワンクリック取り込み
- **✅ 実在性検証**: DOI/URL/arXiv/PubMed の自動チェック、撤回論文の検出
- **📖 既読証跡管理**: PDF 読書記録、ページ番号付き引用カード
- **🎯 ポジション推定**: 査読有無・被引用数・合意度スコア
- **📝 自動整形出力**: APA 7th / IEEE / BibTeX 対応
- **🌐 Next.js Frontend**: モダンなReact UIとFastAPI バックエンド
- **💾 ローカル DB**: SQLite による完全オフライン動作
- **⚖️ 著作権配慮**: API 利用規約準拠、無料枠内運用

---

## 🚀 クイックスタート

### オプション1: Next.js + FastAPI (推奨 🌟)

**モダンなReact UIで使いやすい!**

```powershell
# 1. セットアップ (初回のみ)
.\setup.ps1

# 2. フロントエンド依存関係インストール
cd frontend
npm install
cd ..

# 3. バックエンド + フロントエンド同時起動
.\start-dev.ps1
```

**アクセス:**
- **Frontend UI**: http://localhost:3000 ← こちらにアクセス!
- **Backend API**: http://localhost:8000

### オプション2: FastAPI のみ (シンプル)

```powershell
# 1. セットアップ
.\setup.ps1

# 2. Web UI 起動
.\run.ps1
```

→ http://localhost:8000 にアクセス

---

## 📁 プロジェクト構造

```
seiseiAIchaker/
├── frontend/              # Next.js フロントエンド ⭐ NEW!
│   ├── src/
│   │   ├── app/          # Next.js App Router (pages)
│   │   ├── components/   # React コンポーネント
│   │   └── lib/          # API クライアント
│   ├── package.json
│   ├── tailwind.config.ts
│   └── README.md
├── refsys/                # Python バックエンド
│   ├── __init__.py
│   ├── __main__.py       # エントリーポイント
│   ├── models/           # Pydantic データモデル
│   ├── db/               # データベース層
│   ├── ingest/           # CSL-JSON 取り込み
│   ├── verify/           # 実在性検証
│   ├── readcheck/        # 既読証跡
│   ├── position/         # ポジション分析
│   ├── format/           # 引用整形
│   ├── ui/               # FastAPI REST API
│   └── cli/              # CLI ツール
├── examples/             # サンプルデータ
├── requirements.txt
├── setup.ps1             # Python環境セットアップ
├── start-dev.ps1         # 開発サーバー起動 ⭐ NEW!
├── run.ps1               # FastAPI単体起動
└── README.md
```

---

## 📖 使い方

### Next.js Web UI (推奨)

1. **起動**: `.\start-dev.ps1` でサーバー起動
2. **アクセス**: ブラウザで http://localhost:3000 を開く
3. **インポート**: CSL-JSON ファイルをドラッグ＆ドロップ
4. **検証**: 各文献の詳細ページで「🔍 実在性検証を実行」をクリック
5. **カード作成**: 引用カードを作成して既読証跡を記録
6. **引用生成**: APA/IEEE形式の引用テキストを生成してコピー

### FastAPI Web UI (シンプル)

1. `python -m refsys server` でサーバー起動
2. ブラウザで http://localhost:8000 を開く
3. 同様の操作でシンプルなUIを使用

### CLI (コマンドライン)

```powershell
# データベース初期化
python -m refsys init

# 文献の検証
python -m refsys verify --id <work_id>

# 引用テキスト生成
python -m refsys cite --id <work_id> --format apa

# 引用カード作成
python -m refsys claim --id <work_id> --text "主張テキスト" --context "文脈"

# 監査レポート生成
python -m refsys report --id <work_id>

# サーバー起動
python -m refsys server
```

---

## 🎨 技術スタック

### Frontend (Next.js)
- **Next.js 14** - React フレームワーク (App Router)
- **TypeScript** - 型安全性
- **Tailwind CSS** - ユーティリティファーストCSS
- **Axios** - HTTP クライアント
- **React Hook Form** - フォーム管理
- **React Dropzone** - ファイルアップロード
- **Lucide React** - アイコン

### Backend (Python)
- **FastAPI** - 高速Webフレームワーク
- **SQLite** - 軽量データベース
- **Pydantic** - データバリデーション
- **httpx** - 非同期HTTPクライアント
- **PyMuPDF / pdfminer.six** - PDF処理
- **Click + Rich** - CLI

---

## 🌐 API エンドポイント

### Works (文献)
- `GET /works` - 文献一覧取得
- `GET /works/{id}` - 文献詳細取得
- `POST /works/import` - CSL-JSONインポート
- `POST /works/{id}/verify` - 実在性検証実行

### Verification (検証)
- `GET /works/{id}/checks` - 検証結果取得

### Cards (引用カード)
- `GET /works/{id}/cards` - カード一覧取得
- `POST /works/{id}/cards` - カード作成

### Citations (引用)
- `GET /api/works/{id}/cite?format=apa` - 引用テキスト生成

### Export (エクスポート)
- `POST /export/bibliography` - 参考文献リスト生成

詳細は http://localhost:8000/docs で確認

---

## 📚 ワークフロー例

### 1. Zotero から文献をインポート

1. Zotero で文献を選択
2. 右クリック → "エクスポート" → "CSL JSON"
3. RefSys で `entries.json` をドラッグ＆ドロップ

### 2. 実在性を検証

- 文献詳細ページで「検証」ボタンをクリック
- DOI/URL/arXivの到達性を確認
- 撤回論文の有無をチェック
- 査読状況と引用数を取得

### 3. 既読証跡を記録

- 引用文脈カードを作成
- 主張・引用テキストを入力
- 文脈・コメントを記録
- ページ番号を指定

### 4. 論文に引用

- 引用生成ボタンで APA/IEEE 形式を選択
- 生成されたテキストをコピー
- 論文に貼り付け

---

## 🔧 開発

### Backend 開発

```powershell
# 仮想環境作成
python -m venv venv
venv\Scripts\activate

# 依存関係インストール
pip install -r requirements.txt

# データベース初期化
python -m refsys init

# サーバー起動 (ホットリロード)
uvicorn refsys.ui.app:app --reload
```

### Frontend 開発

```powershell
cd frontend

# 依存関係インストール
npm install

# 開発サーバー起動
npm run dev

# ビルド
npm run build

# 本番サーバー
npm start
```

### テスト

```powershell
# Python テスト
python test_system.py

# 型チェック (Frontend)
cd frontend
npx tsc --noEmit

# Lintチェック
npm run lint
```

---

## 📦 デプロイ

### Vercel (Frontend)

```bash
cd frontend
vercel
```

環境変数: `NEXT_PUBLIC_API_URL=https://your-api-domain.com`

### Docker (Backend)

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY refsys refsys
CMD ["python", "-m", "refsys", "server", "--host", "0.0.0.0"]
```

---

## 📄 ライセンス

MIT License - 詳細は [LICENSE](LICENSE) を参照

**外部API利用規約準拠:**
- Crossref API (無料枠)
- OpenAlex API (無料・オープン)
- arXiv API (無料・オープン)
- PubMed API (無料・オープン)
- Unpaywall API (無料、メールアドレス必須)
- Retraction Watch API (無料)

---

## 🤝 貢献

バグ報告や機能提案は GitHub の Issues へお願いします。

## 📞 サポート

- **ドキュメント**: [USAGE.md](USAGE.md), [QUICKSTART.md](QUICKSTART.md)
- **Frontend ガイド**: [frontend/README.md](frontend/README.md)
- **開発者向け**: [CONTRIBUTING.md](CONTRIBUTING.md)

---

**Made with ❤️ for researchers**
