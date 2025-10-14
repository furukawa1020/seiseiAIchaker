"""
CSL-JSON形式の文献データモデル
"""
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime


class CSLName(BaseModel):
    """CSL名前形式"""
    family: Optional[str] = None
    given: Optional[str] = None
    literal: Optional[str] = None


class CSLDate(BaseModel):
    """CSL日付形式"""
    date_parts: Optional[List[List[int]]] = Field(default=None, alias="date-parts")
    raw: Optional[str] = None
    
    def get_year(self) -> Optional[int]:
        """年を取得"""
        if self.date_parts and len(self.date_parts) > 0:
            if len(self.date_parts[0]) > 0:
                return self.date_parts[0][0]
        if self.raw:
            try:
                return int(self.raw[:4])
            except:
                pass
        return None


class CSLItem(BaseModel):
    """CSL-JSON文献項目"""
    id: str
    type: str  # article-journal, book, chapter, paper-conference, etc.
    title: Optional[str] = None
    author: Optional[List[CSLName]] = None
    editor: Optional[List[CSLName]] = None
    issued: Optional[CSLDate] = None
    container_title: Optional[str] = Field(default=None, alias="container-title")
    volume: Optional[str] = None
    issue: Optional[str] = None
    page: Optional[str] = None
    DOI: Optional[str] = None
    URL: Optional[str] = None
    ISBN: Optional[str] = None
    ISSN: Optional[str] = None
    publisher: Optional[str] = None
    publisher_place: Optional[str] = Field(default=None, alias="publisher-place")
    abstract: Optional[str] = None
    
    # 拡張メタデータ
    arxiv_id: Optional[str] = None
    pubmed_id: Optional[str] = None
    peer_reviewed: Optional[bool] = None
    retracted: bool = False
    consensus_score: Optional[int] = None
    
    class Config:
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "id": "lazarus1984",
                "type": "article-journal",
                "title": "On the relationship between emotion and cognition",
                "author": [
                    {"family": "Lazarus", "given": "Richard S."}
                ],
                "issued": {"date-parts": [[1984]]},
                "container-title": "American Psychologist",
                "volume": "39",
                "issue": "2",
                "page": "124-129",
                "DOI": "10.1037/0003-066X.39.2.124"
            }
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """辞書形式に変換"""
        return self.model_dump(by_alias=True, exclude_none=True)


class WorkCreate(BaseModel):
    """文献作成リクエスト"""
    csl_data: CSLItem
    pdf_path: Optional[str] = None


class WorkUpdate(BaseModel):
    """文献更新リクエスト"""
    title: Optional[str] = None
    peer_reviewed: Optional[bool] = None
    retracted: Optional[bool] = None
    consensus_score: Optional[int] = None
    url: Optional[str] = None


class WorkResponse(BaseModel):
    """文献レスポンス"""
    id: str
    title: str
    type: str
    authors: List[str]
    year: Optional[int]
    doi: Optional[str]
    url: Optional[str]
    peer_reviewed: Optional[bool]
    retracted: bool
    consensus_score: Optional[int]
    created_at: datetime
    
    class Config:
        from_attributes = True
