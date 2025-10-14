# テスト用スクリプト
import asyncio
from refsys.db import init_database
from refsys.ingest import parse_csl_from_json_file, deduplicate_items
from refsys.verify import verify_work, Verifier
from refsys.position import PositionAnalyzer, format_position_summary
from refsys.format import ReferenceFormatter, InTextCitation
from refsys.db.dao import WorkDAO, CheckDAO


async def main():
    print("=== RefSys テスト ===\n")
    
    # 1. データベース初期化
    print("1. データベース初期化...")
    init_database()
    print("✅ 完了\n")
    
    # 2. サンプルデータ読み込み
    print("2. サンプル文献読み込み...")
    items = parse_csl_from_json_file('examples/sample_works.json')
    print(f"✅ {len(items)}件の文献を読み込みました\n")
    
    # 3. 重複排除
    print("3. 重複排除...")
    unique_items, duplicates = deduplicate_items(items)
    print(f"✅ {len(unique_items)}件（重複{len(duplicates)}件除外）\n")
    
    # 4. 位置づけ分析
    print("4. 位置づけ分析...")
    analyzer = PositionAnalyzer()
    for item in unique_items[:1]:  # 最初の1件だけテスト
        metadata = await analyzer.analyze_work(item.to_dict())
        print(format_position_summary(metadata))
        print()
    
    # 5. 実在性検証
    print("5. 実在性検証...")
    async with Verifier() as verifier:
        for item in unique_items[:1]:  # 最初の1件だけテスト
            results = await verify_work(item.to_dict(), verifier)
            print(f"文献: {item.title}")
            for kind, result in results.items():
                print(f"  {kind}: {result.status} - {result.detail}")
    print()
    
    # 6. データベース保存
    print("6. データベースに保存...")
    for item in unique_items:
        try:
            work_id = await WorkDAO.create(item)
            print(f"✅ 保存: {work_id} - {item.title[:50]}")
        except Exception as e:
            print(f"⚠️  スキップ: {e}")
    print()
    
    # 7. 参考文献フォーマット
    print("7. 参考文献フォーマット（APA）...")
    apa_formatter = ReferenceFormatter('apa')
    for item in unique_items:
        ref = apa_formatter.format_reference(item)
        print(f"  {ref}\n")
    
    print("8. 参考文献フォーマット（IEEE）...")
    ieee_formatter = ReferenceFormatter('ieee')
    for item in unique_items:
        ref = ieee_formatter.format_reference(item)
        print(f"  {ref}\n")
    
    # 9. 本文中引用
    print("9. 本文中引用...")
    citation = InTextCitation('apa')
    for item in unique_items:
        cite = citation.cite(item)
        print(f"  {item.title[:40]}... → {cite}")
    print()
    
    print("=== テスト完了 ===")
    print("\nWeb UIを起動するには:")
    print("  python -m refsys server")
    print("\nCLIを使うには:")
    print("  python -m refsys --help")


if __name__ == "__main__":
    asyncio.run(main())
