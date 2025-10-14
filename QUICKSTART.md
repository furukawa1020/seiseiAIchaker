# RefSys クイックスタートガイド

## インストール

```bash
# 依存関係のインストール
pip install -r requirements.txt

# データベース初期化
python -m refsys.db.init_db
```

## 使い方

### 1. CLI使用

#### データベース初期化
```bash
python -m refsys init
```

#### 文献のインポートと検証
```bash
python -m refsys verify --in examples/sample_works.json --update-cache --report verify_report.md
```

#### 参考文献リスト生成（APA形式）
```bash
python -m refsys cite --style apa --in examples/sample_works.json --out references_apa.txt
```

#### 参考文献リスト生成（IEEE形式）
```bash
python -m refsys cite --style ieee --in examples/sample_works.json --out references_ieee.txt
```

#### BibTeX形式でエクスポート
```bash
python -m refsys cite --format bibtex --in examples/sample_works.json --out references.bib
```

#### 引用文脈カード作成
```bash
python -m refsys claim --work-id lazarus1984 --claim "感情と認知の関係性について" --page 125 --evidence "emotion and cognition are fundamentally intertwined" --limitations "サンプルサイズが小さい"
```

#### 監査レポート生成
```bash
python -m refsys report --work-id lazarus1984 --out audit_lazarus1984.md
```

### 2. Web UI使用

```bash
# サーバー起動
python -m refsys server

# ブラウザで http://localhost:8000 を開く
```

#### Web UIでできること
- 文献のインポート（ファイルアップロードまたはJSON入力）
- 実在性検証の実行
- 引用文脈カードの作成
- 既読スコアの確認
- 本文中引用の生成
- 参考文献リストのエクスポート

### 3. Pythonスクリプトから使用

```python
import asyncio
from refsys.ingest import parse_csl_from_json_file
from refsys.verify import verify_work
from refsys.format import ReferenceFormatter

# 文献読み込み
items = parse_csl_from_json_file('examples/sample_works.json')

# 実在性検証
async def verify():
    for item in items:
        results = await verify_work(item.to_dict())
        print(f"{item.title}:")
        for kind, result in results.items():
            print(f"  {kind}: {result.status}")

asyncio.run(verify())

# 参考文献フォーマット
formatter = ReferenceFormatter('apa')
for item in items:
    print(formatter.format_reference(item))
```

## ワークフロー例

### 論文執筆時の完全ワークフロー

1. **文献収集**
   - Zotero, Mendeley等から CSL-JSON でエクスポート
   - または手動でJSON作成

2. **インポート＆検証**
   ```bash
   python -m refsys verify --in my_works.json --update-cache --report verify_report.md
   ```

3. **PDFを読みながら記録**（将来実装予定）
   - PDFビューアで文献を読む
   - ハイライトした箇所を記録

4. **引用文脈カード作成**
   ```bash
   python -m refsys claim --work-id <ID> --claim "..." --page <N> --evidence "..."
   ```
   または Web UI で作成

5. **既読スコア確認**
   - Web UI の文献詳細ページで確認
   - スコアが基準を満たしているか確認

6. **参考文献リスト生成**
   ```bash
   python -m refsys cite --style apa --in my_works.json --out references.txt
   ```

7. **監査レポート出力**
   ```bash
   python -m refsys report --work-id <ID> --out audit.md
   ```

## トラブルシューティング

### データベースエラー
```bash
# データベースを再初期化
rm ~/.refsys/refsys.db
python -m refsys init
```

### 検証タイムアウト
- ネットワーク接続を確認
- キャッシュが古い場合は `--update-cache` を使用

### PDF処理エラー
- PyMuPDF または pdfminer.six がインストールされているか確認
```bash
pip install PyMuPDF pdfminer.six
```

## 設定

環境変数でカスタマイズ可能：

```bash
# データベースパス
export REFSYS_DB_PATH=/custom/path/refsys.db

# キャッシュディレクトリ
export REFSYS_CACHE_DIR=/custom/cache/dir
```

## 次のステップ

- [ ] PDF閲覧ログ機能の実装
- [ ] クイズ自動生成の実装
- [ ] ローカルLLM連携（オプション）
- [ ] チーム共有機能（エクスポート/インポート）
- [ ] 監査レポートのPDF出力

## サポート

問題が発生した場合は、以下を確認してください：
1. Python 3.11以上がインストールされているか
2. すべての依存関係がインストールされているか
3. データベースが初期化されているか

より詳細な情報は README.md を参照してください。
