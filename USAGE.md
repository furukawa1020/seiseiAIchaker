# 📝 使い方の詳細ガイド

## 目次
1. [基本的な使い方](#基本的な使い方)
2. [文献のインポート](#文献のインポート)
3. [実在性検証](#実在性検証)
4. [既読証跡の記録](#既読証跡の記録)
5. [引用文脈カード](#引用文脈カード)
6. [参考文献リスト生成](#参考文献リスト生成)
7. [監査レポート](#監査レポート)
8. [高度な使い方](#高度な使い方)

---

## 基本的な使い方

### セットアップ

```powershell
# セットアップスクリプト実行（推奨）
.\setup.ps1

# または手動セットアップ
pip install -r requirements.txt
python -m refsys.db.init_db
```

### Web UI の起動

```bash
python -m refsys server
```

ブラウザで `http://localhost:8000` を開きます。

---

## 文献のインポート

### CSL-JSON形式とは？

CSL-JSON は Citation Style Language の JSON 表現で、文献管理の標準フォーマットです。

```json
{
  "id": "unique_id",
  "type": "article-journal",
  "title": "論文タイトル",
  "author": [
    {"family": "山田", "given": "太郎"}
  ],
  "issued": {"date-parts": [[2023]]},
  "container-title": "ジャーナル名",
  "volume": "10",
  "issue": "2",
  "page": "100-120",
  "DOI": "10.1234/example"
}
```

### インポート方法

#### 1. Web UI でインポート

1. トップページの「文献のインポート」セクションへ
2. ファイルをアップロード、または JSON を直接貼り付け
3. 「インポート」ボタンをクリック

#### 2. CLI でインポート

```bash
python -m refsys verify --in my_works.json --update-cache
```

#### 3. Zotero からエクスポート

1. Zotero で文献を選択
2. 右クリック → 「項目をエクスポート」
3. 形式: "CSL JSON" を選択
4. ファイルを保存して RefSys にインポート

---

## 実在性検証

### 何が検証されるか？

- **DOI**: DOI.org での解決可否
- **URL**: HTTP ステータスコード確認
- **arXiv ID**: arXiv API での存在確認
- **PubMed ID**: PubMed での存在確認
- **リトラクション**: 撤回・訂正の有無

### 検証の実行

#### Web UI

1. 文献詳細ページを開く
2. 「🔍 実在性検証を実行」ボタンをクリック
3. 結果が表示される

#### CLI

```bash
python -m refsys verify --in works.json --report report.md
```

### 検証結果の見方

- **✅ ok**: 問題なし
- **⚠️ warn**: 警告あり（タイムアウトなど）
- **❌ fail**: 失敗（リンク切れ、撤回など）

### 死リンクへの対応

DOI がある場合、自動的に代替 URL を探します：
- Unpaywall でオープンアクセス版を検索
- 出版社の公式 URL を取得

---

## 既読証跡の記録

### 目的

「本当に読んだ？」を証明できるように、読書の証跡を記録します。

### 記録される情報

1. **ページ滞在時間**: 各ページをどれだけ読んだか
2. **到達率**: ページ末尾まで読んだか
3. **ハイライト**: 重要箇所の抽出
4. **スニペットハッシュ**: 本文断片の検証用ハッシュ

### 既読スコアの基準

- **ページ滞在時間**: 最低 20 秒/ページ
- **到達率**: 90% 以上
- **読了ページ率**: 全体の 80% 以上
- **カード作成**: 最低 1 件

### スコア表示

Web UI の文献詳細ページで確認：
- **0-100 のスコア**
- **✅ PASS** または **⚠️ 要追加作業**

---

## 引用文脈カード

### カードとは？

引用する際に必要な情報を構造化して記録するカードです。

### カードの構成要素

1. **主張**: あなたが論文で使う要点
2. **証拠**: 本文からの引用（30-120文字）
3. **ページ範囲**: 該当箇所
4. **限界・注意点**: 反論や境界条件

### カードの作成

#### Web UI

1. 文献詳細ページを開く
2. 「引用文脈カード」セクションの作成フォームに入力
3. 「カードを作成」ボタンをクリック

#### CLI

```bash
python -m refsys claim \
  --work-id lazarus1984 \
  --claim "感情と認知は相互に関連している" \
  --page 125 \
  --evidence "emotion and cognition are fundamentally intertwined" \
  --limitations "サンプルサイズが小さく、一般化には注意が必要"
```

### カードの完成度

- **✅ 完成**: 全項目が入力され、証拠が 20 文字以上
- **⚠️ 未完成**: 不足している項目がある

---

## 参考文献リスト生成

### サポートする形式

1. **APA 7**: 心理学、教育学など
2. **IEEE**: 工学、情報科学など
3. **BibTeX**: LaTeX 用

### 生成方法

#### Web UI

トップページの「エクスポート」リンクから。

#### CLI - APA 形式

```bash
python -m refsys cite \
  --style apa \
  --in works.json \
  --out references_apa.txt
```

#### CLI - IEEE 形式

```bash
python -m refsys cite \
  --style ieee \
  --in works.json \
  --out references_ieee.txt
```

#### CLI - BibTeX 形式

```bash
python -m refsys cite \
  --format bibtex \
  --in works.json \
  --out references.bib
```

### APA 形式の例

```
Lazarus, R. S. (1984). On the relationship between emotion and cognition. 
*American Psychologist*, *39*(2), 124-129. https://doi.org/10.1037/0003-066X.39.2.124
```

### IEEE 形式の例

```
[1] R. S. Lazarus, "On the relationship between emotion and cognition," 
*American Psychologist*, vol. 39, no. 2, pp. 124-129, 1984. 
doi: 10.1037/0003-066X.39.2.124
```

### 本文中引用の取得

#### Web UI

文献詳細ページで「📝 本文中引用を取得」をクリック。

#### CLI

```bash
# API経由（Web UIサーバー起動中）
curl "http://localhost:8000/api/works/lazarus1984/cite?style=apa&page=125"
```

---

## 監査レポート

### 目的

論文審査や共同研究で「ちゃんと読んだ証拠」を提示するためのレポート。

### 含まれる情報

- 文献の基本情報
- 実在性検証結果
- 既読証跡（ページごと）
- 引用文脈カード一覧
- 主張-証拠-ページの三点対応

### レポート生成

```bash
python -m refsys report \
  --work-id lazarus1984 \
  --out audit_lazarus1984.md
```

生成される Markdown ファイルは、そのまま提出資料として使えます。

---

## 高度な使い方

### Python スクリプトから使用

```python
import asyncio
from refsys.ingest import parse_csl_from_dict
from refsys.verify import verify_work
from refsys.format import ReferenceFormatter

# 文献データ
work_data = {
    "title": "My Paper",
    "author": [{"family": "Doe", "given": "John"}],
    "type": "article-journal",
    "DOI": "10.1234/example"
}

# CSL パース
from refsys.ingest import parse_csl_from_dict
csl = parse_csl_from_dict(work_data)

# 実在性検証
async def verify():
    results = await verify_work(csl.to_dict())
    for kind, result in results.items():
        print(f"{kind}: {result.status}")

asyncio.run(verify())

# 参考文献フォーマット
formatter = ReferenceFormatter('apa')
ref = formatter.format_reference(csl)
print(ref)
```

### バッチ処理

複数の文献を一括処理：

```python
import asyncio
from refsys.ingest import parse_csl_from_json_file
from refsys.verify import verify_work, Verifier
from refsys.db.dao import WorkDAO, CheckDAO

async def batch_import(json_file):
    items = parse_csl_from_json_file(json_file)
    
    async with Verifier() as verifier:
        for item in items:
            # 保存
            work_id = await WorkDAO.create(item)
            
            # 検証
            results = await verify_work(item.to_dict(), verifier)
            
            # 検証結果保存
            for kind, result in results.items():
                await CheckDAO.create(
                    work_id=work_id,
                    kind=result.kind,
                    status=result.status,
                    detail=result.detail,
                    http_code=result.http_code
                )
            
            print(f"✅ {item.title}")

asyncio.run(batch_import('my_works.json'))
```

### カスタムフォーマッタ

独自の引用スタイルを実装：

```python
from refsys.format import ReferenceFormatter

class CustomFormatter(ReferenceFormatter):
    def format_reference(self, csl):
        # カスタムロジック
        return f"{csl.title} ({csl.issued.get_year()})"
```

---

## トラブルシューティング

### 問題: インポートエラー

**原因**: JSON 形式が不正

**解決**:
```python
import json
with open('works.json') as f:
    data = json.load(f)  # ここでエラーが出ればJSON不正
```

### 問題: 検証タイムアウト

**原因**: ネットワーク接続が遅い

**解決**:
- キャッシュを利用: `--update-cache` なしで実行
- タイムアウト値を増やす（コード修正が必要）

### 問題: PDF が読めない

**原因**: PyMuPDF がインストールされていない

**解決**:
```bash
pip install PyMuPDF
```

---

## よくある質問

### Q: 有料APIは使いますか？

**A**: いいえ、すべて無料のAPIのみを使用します。

### Q: PDFの全文は保存されますか？

**A**: ローカルのみで、外部に送信されません。

### Q: 合意度スコアの精度は？

**A**: 目安であり、断定的な評価ではありません。最終判断は人間が行ってください。

### Q: オフラインで使えますか？

**A**: キャッシュがあれば可能です。初回はネット接続が必要です。

---

## 次のステップ

- サンプルデータで試す: `examples/sample_works.json`
- テストを実行: `python test_system.py`
- Web UIで実際に操作してみる

より詳しい情報は README.md と QUICKSTART.md を参照してください。
