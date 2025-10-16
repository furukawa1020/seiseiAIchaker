"""
FastAPI Web UI アプリケーション
"""
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi import Request
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
import json
from typing import List, Optional
import asyncio

from refsys.models import CSLItem
from refsys.ingest import parse_csl_from_dict, parse_csl_from_json_file, deduplicate_items
from refsys.verify import verify_work, Verifier
from refsys.position import PositionAnalyzer, format_position_summary
from refsys.format import ReferenceFormatter, InTextCitation, export_to_bibtex
from refsys.db.dao import WorkDAO, CheckDAO, ClaimCardDAO, ReadEvidenceDAO
from refsys.db.init_db import initialize_database
from refsys.readcheck import ClaimCard, ReadingScorer, ReadingEvidence

app = FastAPI(
    title="RefSys",
    description="正確な参考文献・引用テンプレ自動生成＋実在性/既読検証システム",
    version="0.1.0"
)

@app.on_event("startup")
async def startup_event():
    """アプリケーション起動時にデータベースを初期化"""
    print("🔧 データベースを初期化中...")
    await initialize_database()
    print("✅ データベース初期化完了!")

# CORS設定（Next.jsフロントエンドからのアクセスを許可）
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # Next.js開発サーバー
        "http://127.0.0.1:3000",
        "http://localhost:8000",  # FastAPI自身
        "https://seisei-a-ichaker.vercel.app",  # Vercel本番環境
    ],
    allow_credentials=True,
    allow_methods=["*"],  # GET, POST, PUT, DELETE等すべて許可
    allow_headers=["*"],  # すべてのヘッダーを許可
)

# テンプレートとスタティックファイル
BASE_DIR = Path(__file__).resolve().parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

# スタティックファイル用ディレクトリ作成
static_dir = BASE_DIR / "static"
static_dir.mkdir(exist_ok=True)


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """トップページ"""
    works = await WorkDAO.list_all(limit=50)
    return templates.TemplateResponse(
        "index.html",
        {"request": request, "works": works}
    )


@app.get("/works", response_class=HTMLResponse)
async def list_works(request: Request, limit: int = 50, offset: int = 0):
    """文献リスト"""
    works = await WorkDAO.list_all(limit=limit, offset=offset)
    return templates.TemplateResponse(
        "works_list.html",
        {"request": request, "works": works}
    )


@app.get("/works/{work_id}", response_class=HTMLResponse)
async def work_detail(request: Request, work_id: str):
    """文献詳細"""
    work = await WorkDAO.get(work_id)
    if not work:
        raise HTTPException(status_code=404, detail="Work not found")
    
    # 検証結果取得
    checks = await CheckDAO.get_by_work(work_id)
    
    # 既読証跡取得
    evidences = await ReadEvidenceDAO.get_by_work(work_id)
    
    # カード取得
    cards = await ClaimCardDAO.get_by_work(work_id)
    
    # 既読スコア計算
    scorer = ReadingScorer()
    read_evidences = [
        ReadingEvidence(
            work_id=e['work_id'],
            pdf_path=e['pdf_path'],
            page=e['page'],
            dwell_secs=e['dwell_secs'],
            coverage=e['coverage']
        )
        for e in evidences
    ]
    
    claim_cards = [
        ClaimCard(
            work_id=c['work_id'],
            claim=c['claim'],
            evidence_snippet=c['evidence_snippet'],
            page_from=c['page_from'],
            page_to=c['page_to'],
            limitations=c['limitations'],
            verified=c['verified'],
            card_id=c['id']
        )
        for c in cards
    ]
    
    # ページ数を推定（仮）
    total_pages = max([e['page'] for e in evidences], default=0) + 1
    
    reading_score = scorer.calculate_score(
        evidences=read_evidences,
        total_pages=total_pages,
        cards=claim_cards
    ) if evidences else None
    
    return templates.TemplateResponse(
        "work_detail.html",
        {
            "request": request,
            "work": work,
            "checks": checks,
            "evidences": evidences,
            "cards": cards,
            "reading_score": reading_score
        }
    )


# ============================================
# JSON API エンドポイント（Next.jsフロントエンド用）
# ============================================

@app.get("/api/works")
async def api_list_works(limit: Optional[int] = 100):
    """文献リスト（JSON）"""
    if limit is None:
        limit = 100
    works = await WorkDAO.list_all(limit=limit)
    return works


@app.get("/api/works/{work_id}")
async def api_get_work(work_id: str):
    """文献詳細（JSON）"""
    work = await WorkDAO.get(work_id)
    if not work:
        raise HTTPException(status_code=404, detail="Work not found")
    return work


@app.get("/api/works/{work_id}/checks")
async def api_get_checks(work_id: str):
    """検証結果取得（JSON）"""
    checks = await CheckDAO.get_by_work(work_id)
    return checks


@app.get("/api/works/{work_id}/cards")
async def api_get_cards(work_id: str):
    """引用カード取得（JSON）"""
    cards = await ClaimCardDAO.get_by_work(work_id)
    return cards


@app.get("/api/works/{work_id}/reading-score")
async def api_get_reading_score(work_id: str):
    """既読スコア取得（JSON）"""
    evidences = await ReadEvidenceDAO.get_by_work(work_id)
    cards = await ClaimCardDAO.get_by_work(work_id)
    
    scorer = ReadingScorer()
    read_evidences = [
        ReadingEvidence(
            work_id=e['work_id'],
            pdf_path=e.get('pdf_path', ''),
            page=e.get('page', 0),
            dwell_secs=e.get('dwell_secs', 0),
            coverage=e.get('coverage', 0.0)
        )
        for e in evidences
    ]
    
    claim_cards = [
        ClaimCard(
            work_id=c['work_id'],
            claim_text=c['claim_text'],
            context=c.get('context', ''),
            page_numbers=c.get('page_numbers', '')
        )
        for c in cards
    ]
    
    total_pages = max([e.get('page', 0) for e in evidences], default=0) + 1
    
    score_data = scorer.calculate_score(
        evidences=read_evidences,
        total_pages=total_pages,
        cards=claim_cards
    ) if evidences or cards else {
        'score': 0,
        'card_count': len(cards),
        'evidence_count': len(evidences),
        'passed': False
    }
    
    return score_data


@app.post("/api/works/upload-pdf")
async def upload_pdf(file: UploadFile = File(...)):
    """PDFファイルから文献情報を抽出してインポート"""
    import fitz  # PyMuPDF
    from datetime import datetime
    import tempfile
    import os
    import traceback
    
    try:
        if not file.filename.endswith('.pdf'):
            raise HTTPException(status_code=400, detail="PDFファイルのみアップロード可能です")
        
        # 一時ファイルに保存
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
            content = await file.read()
            tmp_file.write(content)
            tmp_file_path = tmp_file.name
        
        try:
            # PDFを開く
            doc = fitz.open(tmp_file_path)
            metadata = doc.metadata
            
            # メタデータから情報を抽出
            title = metadata.get('title', '') or file.filename.replace('.pdf', '')
            author_str = metadata.get('author', '')
            
            # 著者情報をパース
            authors = []
            if author_str:
                # カンマ区切りまたはセミコロン区切りを想定
                author_parts = author_str.replace(';', ',').split(',')
                for part in author_parts:
                    part = part.strip()
                    if part:
                        # "Family, Given" or "Given Family" 形式に対応
                        if ' ' in part:
                            names = part.split()
                            authors.append({
                                'family': names[-1],
                                'given': ' '.join(names[:-1])
                            })
                        else:
                            authors.append({'family': part, 'given': ''})
            
            if not authors:
                authors = [{'family': 'Unknown', 'given': ''}]
            
            # 発行年を抽出（メタデータまたは作成日から）
            issued_year = None
            if metadata.get('creationDate'):
                try:
                    # "D:20231201..." 形式をパース
                    date_str = metadata['creationDate']
                    if date_str.startswith('D:'):
                        year_str = date_str[2:6]
                        issued_year = int(year_str)
                except:
                    pass
            
            if not issued_year:
                issued_year = datetime.now().year
            
            # ページ数を取得（docを閉じる前に）
            page_count = len(doc)
            
            doc.close()
            
            # 位置づけ分析（CSLItemをdict形式に変換）
            analyzer = PositionAnalyzer()
            work_dict = {
                'id': f"pdf_{datetime.now().strftime('%Y%m%d%H%M%S')}",
                'type': 'article',
                'title': title,
                'author': authors,
                'issued': {'date-parts': [[issued_year]]},
                'abstract': metadata.get('subject', '')
            }
            position = await analyzer.analyze_work(work_dict)
            
            # CSL-JSON形式で作成（位置づけ情報を含む）
            csl_item = CSLItem(
                id=work_dict['id'],
                type='article',
                title=title,
                author=authors,
                issued={'date-parts': [[issued_year]]},
                abstract=metadata.get('subject', ''),
                peer_reviewed=position.peer_reviewed,
                consensus_score=position.consensus_score
            )
            
            # データベースに保存
            work_id = await WorkDAO.create(csl_item)
            
            return {
                'work_id': work_id,
                'title': title,
                'authors': authors,
                'year': issued_year,
                'pages': page_count,
                'message': 'PDFから文献情報を抽出してインポートしました'
            }
            
        except Exception as e:
            error_detail = f"PDF処理エラー: {str(e)}\n{traceback.format_exc()}"
            print(error_detail)  # ログに出力
            raise HTTPException(status_code=500, detail=error_detail)
        finally:
            # 一時ファイルを削除
            if os.path.exists(tmp_file_path):
                os.remove(tmp_file_path)
    
    except HTTPException:
        raise
    except Exception as e:
        error_detail = f"予期しないエラー: {str(e)}\n{traceback.format_exc()}"
        print(error_detail)  # ログに出力
        raise HTTPException(status_code=500, detail=error_detail)


@app.post("/api/works/import")
async def import_works(
    file: Optional[UploadFile] = File(None),
    json_data: Optional[str] = Form(None)
):
    """文献インポート（CSL-JSON）"""
    items = []
    
    if file:
        # ファイルアップロード
        content = await file.read()
        
        # PDFファイルの場合は別エンドポイントを案内
        if file.filename.endswith('.pdf'):
            raise HTTPException(
                status_code=400, 
                detail="PDFファイルは /api/works/upload-pdf エンドポイントを使用してください"
            )
        
        data = json.loads(content.decode('utf-8'))
        
        if isinstance(data, list):
            for item_data in data:
                items.append(parse_csl_from_dict(item_data))
        elif isinstance(data, dict):
            items.append(parse_csl_from_dict(data))
    
    elif json_data:
        # フォームからのJSON
        data = json.loads(json_data)
        items.append(parse_csl_from_dict(data))
    
    if not items:
        raise HTTPException(status_code=400, detail="No data provided")
    
    # 重複排除
    unique_items, duplicates = deduplicate_items(items)
    
    # データベースに保存
    created_ids = []
    for item in unique_items:
        try:
            # 位置づけ分析
            analyzer = PositionAnalyzer()
            position = await analyzer.analyze_work(item.to_dict())
            
            item.peer_reviewed = position.peer_reviewed
            item.consensus_score = position.consensus_score
            
            # 保存
            work_id = await WorkDAO.create(item)
            created_ids.append(work_id)
            
            # 実在性検証を非同期で実行
            asyncio.create_task(verify_and_save(work_id, item.to_dict()))
        
        except Exception as e:
            print(f"Error importing work: {e}")
    
    return {
        "imported": len(created_ids),
        "duplicates": len(duplicates),
        "work_ids": created_ids
    }


async def verify_and_save(work_id: str, work_data: dict):
    """検証を実行して保存"""
    try:
        results = await verify_work(work_data)
        
        for kind, result in results.items():
            await CheckDAO.create(
                work_id=work_id,
                kind=result.kind,
                status=result.status,
                detail=result.detail,
                http_code=result.http_code
            )
    except Exception as e:
        print(f"Verification error for {work_id}: {e}")


@app.post("/api/works/{work_id}/verify")
async def api_verify_work(work_id: str):
    """文献の実在性検証（JSON）"""
    work = await WorkDAO.get(work_id)
    if not work:
        raise HTTPException(status_code=404, detail="Work not found")
    
    # CSL-JSONを復元
    csl_data = json.loads(work['raw_csl_json'])
    
    # 検証実行
    results = await verify_work(csl_data)
    
    # 保存
    for kind, result in results.items():
        await CheckDAO.create(
            work_id=work_id,
            kind=result.kind,
            status=result.status,
            detail=result.detail,
            http_code=result.http_code
        )
    
    return {
        "work_id": work_id,
        "results": {k: v.to_dict() for k, v in results.items()}
    }


@app.post("/api/works/{work_id}/cards")
async def api_create_claim_card(
    work_id: str,
    claim_text: str = Form(...),
    context: str = Form(...),
    page_numbers: Optional[str] = Form(None)
):
    """引用カード作成（JSON）"""
    work = await WorkDAO.get(work_id)
    if not work:
        raise HTTPException(status_code=404, detail="Work not found")
    
    card_id = await ClaimCardDAO.create(
        work_id=work_id,
        claim_text=claim_text,
        context=context,
        page_numbers=page_numbers
    )
    
    card = await ClaimCardDAO.get(card_id)
    return card


@app.post("/api/works/{work_id}/reading-evidence")
async def api_submit_reading_evidence(
    work_id: str,
    page_numbers: str = Form(...),
    notes: Optional[str] = Form(None)
):
    """既読証跡提出（JSON）"""
    work = await WorkDAO.get(work_id)
    if not work:
        raise HTTPException(status_code=404, detail="Work not found")
    
    # ページ番号をパース
    pages = []
    for part in page_numbers.split(','):
        part = part.strip()
        if '-' in part:
            start, end = map(int, part.split('-'))
            pages.extend(range(start, end + 1))
        else:
            pages.append(int(part))
    
    # 各ページの証跡を記録
    evidence_ids = []
    for page in pages:
        evidence_id = await ReadEvidenceDAO.create(
            work_id=work_id,
            pdf_path='',  # オプション
            page=page,
            dwell_secs=60,  # デフォルト
            coverage=0.5  # デフォルト
        )
        evidence_ids.append(evidence_id)
    
    return {
        "work_id": work_id,
        "pages": pages,
        "evidence_count": len(evidence_ids)
    }


@app.get("/api/works/{work_id}/cite")
async def api_get_citation(work_id: str, format: str = 'apa'):
    """引用テキスト生成（JSON）"""
    work = await WorkDAO.get(work_id)
    if not work:
        raise HTTPException(status_code=404, detail="Work not found")
    
    csl_json = json.loads(work['raw_csl_json'])
    
    formatter = ReferenceFormatter()
    
    if format == 'bibtex':
        citation = export_to_bibtex([csl_json])
    else:
        # CSLItemオブジェクトに変換
        from refsys.ingest import parse_csl_from_dict
        csl_item = parse_csl_from_dict(csl_json)
        # format_referenceメソッドを使用（APA形式）
        citation = formatter.format_reference(csl_item)
    
    return {"citation": citation}


@app.post("/api/export/bibliography")
async def api_export_bibliography(
    work_ids: List[str],
    format: str = 'apa'
):
    """参考文献リストエクスポート（JSON）"""
    from refsys.ingest import parse_csl_from_dict
    
    csl_items = []
    for work_id in work_ids:
        work = await WorkDAO.get(work_id)
        if work:
            csl_json = json.loads(work['raw_csl_json'])
            csl_item = parse_csl_from_dict(csl_json)
            csl_items.append(csl_item)
    
    formatter = ReferenceFormatter()
    
    if format == 'bibtex':
        bibliography = export_to_bibtex([item.to_dict() for item in csl_items])
    else:
        # format_bibliographyメソッドを使用（APA形式）
        bibliography = formatter.format_bibliography(csl_items)
    
    return {"bibliography": bibliography}


# ============================================
# 以下、既存のHTMLエンドポイント
# ============================================

@app.post("/works/{work_id}/verify")
async def verify_work_endpoint(work_id: str):
    """文献の実在性検証"""
    work = await WorkDAO.get(work_id)
    if not work:
        raise HTTPException(status_code=404, detail="Work not found")
    
    # CSL-JSONを復元
    csl_data = json.loads(work['raw_csl_json'])
    
    # 検証実行
    results = await verify_work(csl_data)
    
    # 保存
    for kind, result in results.items():
        await CheckDAO.create(
            work_id=work_id,
            kind=result.kind,
            status=result.status,
            detail=result.detail,
            http_code=result.http_code
        )
    
    return {
        "work_id": work_id,
        "results": {k: v.to_dict() for k, v in results.items()}
    }


@app.post("/works/{work_id}/cards")
async def create_claim_card(
    work_id: str,
    claim: str = Form(...),
    evidence_snippet: str = Form(...),
    page_from: int = Form(...),
    page_to: Optional[int] = Form(None),
    limitations: Optional[str] = Form(None)
):
    """引用文脈カード作成"""
    card = ClaimCard(
        work_id=work_id,
        claim=claim,
        evidence_snippet=evidence_snippet,
        page_from=page_from,
        page_to=page_to,
        limitations=limitations
    )
    
    card_id = await ClaimCardDAO.create(
        card_id=card.id,
        work_id=card.work_id,
        claim=card.claim,
        evidence_snippet=card.evidence_snippet,
        page_from=card.page_from,
        page_to=card.page_to,
        limitations=card.limitations,
        verified=card.verified
    )
    
    return {"card_id": card_id, "is_complete": card.is_complete()}


@app.get("/export/bibliography")
async def export_bibliography(
    style: str = "apa",
    format: str = "text",
    limit: int = 100
):
    """参考文献リストのエクスポート"""
    works = await WorkDAO.list_all(limit=limit)
    
    # CSL-JSONに変換
    items = []
    for work in works:
        csl_data = json.loads(work['raw_csl_json'])
        items.append(CSLItem(**csl_data))
    
    if format == "bibtex":
        output = export_to_bibtex(items)
        return {"format": "bibtex", "content": output}
    
    else:
        # text (APA or IEEE)
        formatter = ReferenceFormatter(style)
        output = formatter.format_bibliography(items)
        return {"format": style, "content": output}


@app.get("/api/works/{work_id}/cite")
async def get_citation(work_id: str, style: str = "apa", page: Optional[str] = None):
    """本文中引用の取得"""
    work = await WorkDAO.get(work_id)
    if not work:
        raise HTTPException(status_code=404, detail="Work not found")
    
    csl_data = json.loads(work['raw_csl_json'])
    csl = CSLItem(**csl_data)
    
    citation = InTextCitation(style)
    cite_text = citation.cite(csl, page)
    
    return {"citation": cite_text, "style": style}


@app.get("/health")
async def health_check():
    """ヘルスチェック"""
    return {"status": "ok", "version": "0.1.0"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
