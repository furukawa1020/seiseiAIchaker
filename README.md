# 正確な参考文献・引用テンプレ自動生成＋実在性/既読検証システム

## 概要
AI時代の学術引用支援システム。実在する文献のみを引用し、既読証跡を記録し、参考文献を自動整形します。

## 特徴
- ✅ **実在性検証**: DOI/URL/arXiv/PubMed/ISBNの検証と到達性確認
- ✅ **既読証跡**: PDF閲覧ログ、ハイライト、引用文脈カード
- ✅ **位置づけ判定**: 査読有無、引用数、合意度スコア
- ✅ **自動整形**: APA7 / IEEE形式の参考文献リスト生成
- ✅ **監査可能**: すべての検証結果と既読証跡を記録
- 🚫 **無料・ローカル優先**: 外部有料API不使用、CPU環境で動作

## インストール

```bash
# 依存関係のインストール
pip install -r requirements.txt

# データベース初期化
python -m refsys.db.init_db

# Web UIの起動
python -m refsys.ui.app
```

## 使い方

### CLI
```bash
# 文献のインポートと検証
refsys verify --in entries.json --update-cache --report verify_report.md

# PDF既読ログ記録
refsys readlog --pdf ./papers/paper.pdf --work-id <UUID>

# 引用文脈カード作成
refsys claim --work-id <UUID> --claim "本研究で用いる定義は..." --page 12-13

# 参考文献出力
refsys cite --style apa --in entries.json --out refs_apa.txt

# 監査レポート生成
refsys report --work-id <UUID> --out audit.md
```

### Web UI
```bash
python -m refsys.ui.app
# ブラウザで http://localhost:8000 を開く
```

## プロジェクト構造
```
refsys/
├── ingest/      # 入力正規化、CSL変換、重複排除
├── verify/      # 実在性検証、死リンク検出
├── readcheck/   # 既読証跡、ページ滞在、カード管理
├── position/    # 査読判定、引用数、合意度スコア
├── format/      # APA/IEEE整形、エクスポート
├── ui/          # FastAPI Web UI
└── db/          # SQLiteスキーマ、DAO
```

## ライセンス
MIT License

## 注意事項
- PDF全文はローカルのみ保持、外部送信しません
- APIの利用規約を遵守しています
- 合意度スコアは目安であり、断定的な判断ではありません
