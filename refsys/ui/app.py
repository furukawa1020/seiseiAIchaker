"""
FastAPI Web UI アプリケーション
"""
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi import Request
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
from refsys.readcheck import ClaimCard, ReadingScorer, ReadingEvidence

app = FastAPI(
    title="RefSys",
    description="正確な参考文献・引用テンプレ自動生成＋実在性/既読検証システム",
    version="0.1.0"
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


@app.post("/works/import")
async def import_works(
    file: Optional[UploadFile] = File(None),
    json_data: Optional[str] = Form(None)
):
    """文献インポート"""
    items = []
    
    if file:
        # ファイルアップロード
        content = await file.read()
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
