"""
文献データの取り込み・正規化・重複排除
"""
import re
import json
import uuid
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
from refsys.models import CSLItem, CSLName, CSLDate
import hashlib


def generate_work_id(csl: CSLItem) -> str:
    """文献IDの生成（DOI優先、なければタイトル+著者+年のハッシュ）"""
    if csl.DOI:
        # DOIを正規化してIDに使用
        normalized_doi = csl.DOI.lower().strip()
        return f"doi_{hashlib.md5(normalized_doi.encode()).hexdigest()[:12]}"
    
    # タイトル+第一著者+年でハッシュ生成
    parts = []
    if csl.title:
        parts.append(csl.title.lower().strip())
    if csl.author and len(csl.author) > 0:
        author = csl.author[0]
        if author.family:
            parts.append(author.family.lower().strip())
    if csl.issued:
        year = csl.issued.get_year()
        if year:
            parts.append(str(year))
    
    if parts:
        combined = "_".join(parts)
        return f"work_{hashlib.md5(combined.encode()).hexdigest()[:12]}"
    
    # フォールバック: ランダムUUID
    return f"work_{uuid.uuid4().hex[:12]}"


def normalize_doi(doi: Optional[str]) -> Optional[str]:
    """DOIの正規化"""
    if not doi:
        return None
    
    # https://doi.org/ や http://dx.doi.org/ を削除
    doi = re.sub(r'^https?://(dx\.)?doi\.org/', '', doi, flags=re.IGNORECASE)
    doi = doi.strip()
    
    # DOI形式の検証
    if re.match(r'^10\.\d{4,9}/[-._;()/:A-Z0-9]+$', doi, re.IGNORECASE):
        return doi
    
    return None


def normalize_arxiv(arxiv_id: Optional[str]) -> Optional[str]:
    """arXiv IDの正規化"""
    if not arxiv_id:
        return None
    
    # arXiv: プレフィックスを削除
    arxiv_id = re.sub(r'^arxiv:\s*', '', arxiv_id, flags=re.IGNORECASE)
    arxiv_id = arxiv_id.strip()
    
    # 新形式: YYMM.NNNNN or YYMM.NNNNNVN
    if re.match(r'^\d{4}\.\d{4,5}(v\d+)?$', arxiv_id):
        return arxiv_id
    
    # 旧形式: arch-ive/YYMMNNN
    if re.match(r'^[a-z-]+/\d{7}$', arxiv_id, re.IGNORECASE):
        return arxiv_id
    
    return None


def normalize_pubmed(pubmed_id: Optional[str]) -> Optional[str]:
    """PubMed IDの正規化"""
    if not pubmed_id:
        return None
    
    # PMID: プレフィックスを削除
    pubmed_id = re.sub(r'^pmid:\s*', '', pubmed_id, flags=re.IGNORECASE)
    pubmed_id = pubmed_id.strip()
    
    # 数字のみか確認
    if re.match(r'^\d+$', pubmed_id):
        return pubmed_id
    
    return None


def normalize_isbn(isbn: Optional[str]) -> Optional[str]:
    """ISBNの正規化"""
    if not isbn:
        return None
    
    # ハイフン、スペースを削除
    isbn = re.sub(r'[-\s]', '', isbn)
    
    # ISBN-10 or ISBN-13
    if re.match(r'^\d{9}[\dX]$', isbn, re.IGNORECASE):  # ISBN-10
        return isbn.upper()
    if re.match(r'^\d{13}$', isbn):  # ISBN-13
        return isbn
    
    return None


def parse_csl_from_dict(data: Dict[str, Any]) -> CSLItem:
    """辞書からCSL-JSONをパース"""
    # IDがなければ生成
    if 'id' not in data:
        data['id'] = f"temp_{uuid.uuid4().hex[:8]}"
    
    csl = CSLItem(**data)
    
    # 正規化
    csl.DOI = normalize_doi(csl.DOI)
    csl.arxiv_id = normalize_arxiv(csl.arxiv_id)
    csl.pubmed_id = normalize_pubmed(csl.pubmed_id)
    csl.ISBN = normalize_isbn(csl.ISBN)
    
    # IDの再生成（正規化後）
    csl.id = generate_work_id(csl)
    
    return csl


def parse_csl_from_json_file(filepath: str) -> List[CSLItem]:
    """JSONファイルからCSL-JSONをパース"""
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    items = []
    if isinstance(data, list):
        for item in data:
            items.append(parse_csl_from_dict(item))
    elif isinstance(data, dict):
        items.append(parse_csl_from_dict(data))
    
    return items


def detect_duplicates(items: List[CSLItem]) -> Dict[str, List[int]]:
    """重複の検出（DOI、タイトル類似度による）"""
    duplicates = {}
    
    # DOIベースの重複検出
    doi_map = {}
    for idx, item in enumerate(items):
        if item.DOI:
            doi = item.DOI.lower()
            if doi in doi_map:
                key = f"doi_{doi}"
                if key not in duplicates:
                    duplicates[key] = [doi_map[doi]]
                duplicates[key].append(idx)
            else:
                doi_map[doi] = idx
    
    # タイトル+著者+年ベースの重複検出
    signature_map = {}
    for idx, item in enumerate(items):
        if not item.DOI:  # DOIがある場合はスキップ（すでにチェック済み）
            signature = _create_signature(item)
            if signature in signature_map:
                key = f"sig_{signature[:16]}"
                if key not in duplicates:
                    duplicates[key] = [signature_map[signature]]
                duplicates[key].append(idx)
            else:
                signature_map[signature] = idx
    
    return duplicates


def _create_signature(item: CSLItem) -> str:
    """文献のシグネチャ作成（タイトル+著者+年）"""
    parts = []
    
    if item.title:
        # タイトルを正規化（小文字、記号削除）
        title_norm = re.sub(r'[^\w\s]', '', item.title.lower())
        title_norm = ' '.join(title_norm.split())
        parts.append(title_norm)
    
    if item.author and len(item.author) > 0:
        author = item.author[0]
        if author.family:
            parts.append(author.family.lower())
    
    if item.issued:
        year = item.issued.get_year()
        if year:
            parts.append(str(year))
    
    return hashlib.md5('_'.join(parts).encode()).hexdigest()


def merge_duplicates(items: List[CSLItem], duplicates: Dict[str, List[int]]) -> List[CSLItem]:
    """重複をマージして一意のリストを返す"""
    to_remove = set()
    
    for dup_indices in duplicates.values():
        # 最初のものを残し、他は削除
        # TODO: より賢いマージロジック（メタデータの補完など）
        for idx in dup_indices[1:]:
            to_remove.add(idx)
    
    # 削除対象以外を返す
    return [item for idx, item in enumerate(items) if idx not in to_remove]


def deduplicate_items(items: List[CSLItem]) -> Tuple[List[CSLItem], Dict[str, List[int]]]:
    """重複排除を実行"""
    duplicates = detect_duplicates(items)
    unique_items = merge_duplicates(items, duplicates)
    return unique_items, duplicates


def extract_metadata_from_pdf(pdf_path: str) -> Dict[str, Any]:
    """PDFからメタデータを抽出（タイトル、著者など）"""
    try:
        import fitz  # PyMuPDF
        
        doc = fitz.open(pdf_path)
        metadata = doc.metadata
        
        result = {
            "title": metadata.get("title"),
            "author": metadata.get("author"),
            "subject": metadata.get("subject"),
            "keywords": metadata.get("keywords"),
            "creator": metadata.get("creator"),
            "producer": metadata.get("producer"),
        }
        
        doc.close()
        return {k: v for k, v in result.items() if v}
    
    except ImportError:
        # PyMuPDFがない場合はpdfminerを試す
        try:
            from pdfminer.high_level import extract_text
            from pdfminer.pdfparser import PDFParser
            from pdfminer.pdfdocument import PDFDocument
            
            with open(pdf_path, 'rb') as f:
                parser = PDFParser(f)
                doc = PDFDocument(parser)
                
                if doc.info:
                    info = doc.info[0] if isinstance(doc.info, list) else doc.info
                    return {
                        k.decode() if isinstance(k, bytes) else k: 
                        v.decode() if isinstance(v, bytes) else v
                        for k, v in info.items()
                    }
            
            return {}
        except:
            return {}
    except:
        return {}


if __name__ == "__main__":
    # テスト
    test_data = {
        "title": "Test Article",
        "type": "article-journal",
        "author": [{"family": "Doe", "given": "John"}],
        "issued": {"date-parts": [[2023]]},
        "DOI": "10.1234/test.2023"
    }
    
    csl = parse_csl_from_dict(test_data)
    print(f"Generated ID: {csl.id}")
    print(f"Normalized DOI: {csl.DOI}")
