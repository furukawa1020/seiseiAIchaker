"""
RefSys CLI - コマンドラインインターフェース
"""
import click
import asyncio
import json
from pathlib import Path
from rich.console import Console
from rich.table import Table
from rich.progress import track

from refsys.ingest import parse_csl_from_json_file, deduplicate_items
from refsys.verify import verify_work, Verifier
from refsys.position import PositionAnalyzer, format_position_summary
from refsys.format import ReferenceFormatter, export_to_bibtex
from refsys.db.dao import WorkDAO, CheckDAO, ClaimCardDAO
from refsys.db import init_database
from refsys.readcheck import ClaimCard

console = Console()


@click.group()
def cli():
    """RefSys: 正確な参考文献・引用テンプレ自動生成＋実在性/既読検証システム"""
    pass


@cli.command()
def init():
    """データベースを初期化"""
    try:
        init_database()
        console.print("✅ データベースを初期化しました", style="green")
    except Exception as e:
        console.print(f"❌ エラー: {e}", style="red")


@cli.command()
@click.option('--in', 'input_file', required=True, type=click.Path(exists=True), help='入力CSL-JSONファイル')
@click.option('--update-cache', is_flag=True, help='キャッシュを更新')
@click.option('--report', type=click.Path(), help='検証レポートの出力先')
def verify(input_file, update_cache, report):
    """文献の実在性検証"""
    console.print(f"📖 文献を読み込み中: {input_file}", style="cyan")
    
    try:
        items = parse_csl_from_json_file(input_file)
        console.print(f"✅ {len(items)}件の文献を読み込みました", style="green")
        
        # 重複排除
        unique_items, duplicates = deduplicate_items(items)
        if duplicates:
            console.print(f"⚠️  {len(duplicates)}件の重複を除外しました", style="yellow")
        
        # 検証実行
        console.print("\n🔍 実在性検証を実行中...", style="cyan")
        
        async def run_verification():
            results = {}
            async with Verifier() as verifier:
                for item in track(unique_items, description="検証中..."):
                    item_results = await verify_work(item.to_dict(), verifier)
                    results[item.id] = {
                        'item': item,
                        'results': item_results
                    }
            return results
        
        all_results = asyncio.run(run_verification())
        
        # 結果表示
        table = Table(title="検証結果サマリー")
        table.add_column("文献ID", style="cyan")
        table.add_column("タイトル", style="white")
        table.add_column("DOI", style="blue")
        table.add_column("URL", style="green")
        table.add_column("リトラクション", style="yellow")
        
        for work_id, data in all_results.items():
            item = data['item']
            results = data['results']
            
            doi_status = results.get('doi', None)
            url_status = results.get('url', None)
            retract_status = results.get('retraction', None)
            
            table.add_row(
                work_id[:12],
                item.title[:50] if item.title else "-",
                doi_status.status if doi_status else "-",
                url_status.status if url_status else "-",
                "⚠️" if retract_status and retract_status.status == 'fail' else "✅"
            )
        
        console.print(table)
        
        # レポート出力
        if report:
            with open(report, 'w', encoding='utf-8') as f:
                f.write("# 実在性検証レポート\n\n")
                f.write(f"検証日時: {asyncio.get_event_loop().time()}\n\n")
                
                for work_id, data in all_results.items():
                    item = data['item']
                    results = data['results']
                    
                    f.write(f"## {item.title}\n\n")
                    f.write(f"- **ID**: {work_id}\n")
                    if item.DOI:
                        f.write(f"- **DOI**: {item.DOI}\n")
                    if item.URL:
                        f.write(f"- **URL**: {item.URL}\n")
                    
                    f.write("\n### 検証結果\n\n")
                    for kind, result in results.items():
                        f.write(f"- **{kind}**: {result.status} - {result.detail}\n")
                    
                    f.write("\n---\n\n")
            
            console.print(f"✅ レポートを出力しました: {report}", style="green")
    
    except Exception as e:
        console.print(f"❌ エラー: {e}", style="red")
        raise


@cli.command()
@click.option('--style', type=click.Choice(['apa', 'ieee']), default='apa', help='引用スタイル')
@click.option('--in', 'input_file', required=True, type=click.Path(exists=True), help='入力CSL-JSONファイル')
@click.option('--out', 'output_file', required=True, type=click.Path(), help='出力先ファイル')
@click.option('--format', 'output_format', type=click.Choice(['text', 'bibtex']), default='text', help='出力形式')
def cite(style, input_file, output_file, output_format):
    """参考文献リストを生成"""
    console.print(f"📖 文献を読み込み中: {input_file}", style="cyan")
    
    try:
        items = parse_csl_from_json_file(input_file)
        console.print(f"✅ {len(items)}件の文献を読み込みました", style="green")
        
        # フォーマット
        if output_format == 'bibtex':
            output = export_to_bibtex(items)
        else:
            formatter = ReferenceFormatter(style)
            output = formatter.format_bibliography(items)
        
        # 出力
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(output)
        
        console.print(f"✅ 参考文献リストを出力しました: {output_file}", style="green")
        console.print(f"スタイル: {style.upper()}, 形式: {output_format}", style="blue")
    
    except Exception as e:
        console.print(f"❌ エラー: {e}", style="red")
        raise


@cli.command()
@click.option('--work-id', required=True, help='文献ID')
@click.option('--claim', required=True, help='主張')
@click.option('--page', required=True, type=int, help='ページ番号')
@click.option('--evidence', required=True, help='証拠の断片')
@click.option('--limitations', help='限界・注意点')
def claim(work_id, claim, page, evidence, limitations):
    """引用文脈カードを作成"""
    try:
        card = ClaimCard(
            work_id=work_id,
            claim=claim,
            evidence_snippet=evidence,
            page_from=page,
            limitations=limitations
        )
        
        async def save_card():
            return await ClaimCardDAO.create(
                card_id=card.id,
                work_id=card.work_id,
                claim=card.claim,
                evidence_snippet=card.evidence_snippet,
                page_from=card.page_from,
                page_to=card.page_to,
                limitations=card.limitations,
                verified=card.verified
            )
        
        card_id = asyncio.run(save_card())
        
        console.print(f"✅ カードを作成しました: {card_id}", style="green")
        console.print(f"完成度: {'✅ 完成' if card.is_complete() else '⚠️ 未完成'}", 
                     style="green" if card.is_complete() else "yellow")
    
    except Exception as e:
        console.print(f"❌ エラー: {e}", style="red")
        raise


@cli.command()
@click.option('--work-id', required=True, help='文献ID')
@click.option('--out', 'output_file', required=True, type=click.Path(), help='出力先ファイル')
def report(work_id, output_file):
    """監査レポートを生成"""
    try:
        async def generate_report():
            work = await WorkDAO.get(work_id)
            if not work:
                raise ValueError(f"文献が見つかりません: {work_id}")
            
            checks = await CheckDAO.get_by_work(work_id)
            cards = await ClaimCardDAO.get_by_work(work_id)
            
            return work, checks, cards
        
        work, checks, cards = asyncio.run(generate_report())
        
        # Markdownレポート生成
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(f"# 監査レポート: {work['title']}\n\n")
            f.write(f"**文献ID**: {work_id}\n\n")
            
            f.write("## 基本情報\n\n")
            f.write(f"- **タイトル**: {work['title']}\n")
            f.write(f"- **タイプ**: {work['type']}\n")
            if work['issued_year']:
                f.write(f"- **発行年**: {work['issued_year']}\n")
            if work['doi']:
                f.write(f"- **DOI**: {work['doi']}\n")
            
            f.write("\n## 実在性検証結果\n\n")
            if checks:
                for check in checks:
                    f.write(f"- **{check['kind']}**: {check['status']}\n")
                    f.write(f"  - {check['detail']}\n")
            else:
                f.write("*検証未実施*\n")
            
            f.write("\n## 引用文脈カード\n\n")
            if cards:
                for i, card in enumerate(cards, 1):
                    f.write(f"### カード {i}\n\n")
                    f.write(f"- **主張**: {card['claim']}\n")
                    f.write(f"- **証拠**: {card['evidence_snippet']}\n")
                    f.write(f"- **ページ**: {card['page_from']}")
                    if card['page_to'] != card['page_from']:
                        f.write(f"-{card['page_to']}")
                    f.write("\n")
                    if card['limitations']:
                        f.write(f"- **限界**: {card['limitations']}\n")
                    f.write(f"- **検証済み**: {'✅' if card['verified'] else '❌'}\n\n")
            else:
                f.write("*カード未作成*\n")
        
        console.print(f"✅ 監査レポートを出力しました: {output_file}", style="green")
    
    except Exception as e:
        console.print(f"❌ エラー: {e}", style="red")
        raise


@cli.command()
def server():
    """Web UIサーバーを起動"""
    console.print("🚀 RefSys Web UIを起動中...", style="cyan")
    console.print("📍 http://localhost:8000", style="green")
    
    import uvicorn
    from refsys.ui.app import app
    
    uvicorn.run(app, host="0.0.0.0", port=8000)


if __name__ == "__main__":
    cli()
