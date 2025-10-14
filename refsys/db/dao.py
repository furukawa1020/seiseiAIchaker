"""
データアクセスオブジェクト: 文献データのCRUD操作
"""
import json
from typing import List, Dict, Any, Optional
from datetime import datetime
import aiosqlite
from refsys.db import get_async_connection
from refsys.models import CSLItem


class WorkDAO:
    """文献データアクセス"""
    
    @staticmethod
    async def create(csl: CSLItem) -> str:
        """文献を作成"""
        conn = await get_async_connection()
        try:
            # 文献レコード挿入
            year = csl.issued.get_year() if csl.issued else None
            
            await conn.execute(
                """
                INSERT INTO works (
                    id, title, type, container_title, issued_year,
                    doi, url, arxiv_id, pubmed_id, isbn,
                    peer_reviewed, retracted, consensus_score, raw_csl_json
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    csl.id, csl.title, csl.type, csl.container_title, year,
                    csl.DOI, csl.URL, csl.arxiv_id, csl.pubmed_id, csl.ISBN,
                    csl.peer_reviewed, csl.retracted, csl.consensus_score,
                    json.dumps(csl.to_dict())
                )
            )
            
            # 著者の挿入
            if csl.author:
                for ord_num, author in enumerate(csl.author):
                    author_id = await WorkDAO._get_or_create_author(
                        conn,
                        author.family,
                        author.given
                    )
                    await conn.execute(
                        "INSERT INTO work_authors (work_id, author_id, ord) VALUES (?, ?, ?)",
                        (csl.id, author_id, ord_num)
                    )
            
            await conn.commit()
            return csl.id
        
        finally:
            await conn.close()
    
    @staticmethod
    async def _get_or_create_author(
        conn: aiosqlite.Connection,
        family: Optional[str],
        given: Optional[str]
    ) -> int:
        """著者を取得または作成"""
        # 既存チェック
        cursor = await conn.execute(
            "SELECT id FROM authors WHERE family = ? AND given = ?",
            (family, given)
        )
        row = await cursor.fetchone()
        
        if row:
            return row[0]
        
        # 新規作成
        cursor = await conn.execute(
            "INSERT INTO authors (family, given) VALUES (?, ?)",
            (family, given)
        )
        return cursor.lastrowid
    
    @staticmethod
    async def get(work_id: str) -> Optional[Dict[str, Any]]:
        """文献を取得"""
        conn = await get_async_connection()
        try:
            cursor = await conn.execute(
                "SELECT * FROM works WHERE id = ?",
                (work_id,)
            )
            row = await cursor.fetchone()
            
            if not row:
                return None
            
            work = dict(row)
            
            # 著者を取得
            cursor = await conn.execute(
                """
                SELECT a.family, a.given
                FROM authors a
                JOIN work_authors wa ON a.id = wa.author_id
                WHERE wa.work_id = ?
                ORDER BY wa.ord
                """,
                (work_id,)
            )
            authors = await cursor.fetchall()
            work['authors'] = [
                {'family': a[0], 'given': a[1]}
                for a in authors
            ]
            
            return work
        
        finally:
            await conn.close()
    
    @staticmethod
    async def list_all(limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        """全文献をリスト"""
        conn = await get_async_connection()
        try:
            cursor = await conn.execute(
                """
                SELECT id, title, type, issued_year, doi, peer_reviewed, 
                       retracted, consensus_score
                FROM works
                ORDER BY created_at DESC
                LIMIT ? OFFSET ?
                """,
                (limit, offset)
            )
            rows = await cursor.fetchall()
            
            works = []
            for row in rows:
                work = dict(row)
                
                # 著者を取得
                cursor = await conn.execute(
                    """
                    SELECT a.family, a.given
                    FROM authors a
                    JOIN work_authors wa ON a.id = wa.author_id
                    WHERE wa.work_id = ?
                    ORDER BY wa.ord
                    """,
                    (work['id'],)
                )
                authors = await cursor.fetchall()
                work['authors'] = [
                    f"{a[1]} {a[0]}" if a[1] else a[0]
                    for a in authors
                ]
                
                works.append(work)
            
            return works
        
        finally:
            await conn.close()
    
    @staticmethod
    async def update(work_id: str, updates: Dict[str, Any]) -> bool:
        """文献を更新"""
        conn = await get_async_connection()
        try:
            set_clauses = []
            values = []
            
            for key, value in updates.items():
                if key in ['title', 'url', 'peer_reviewed', 'retracted', 'consensus_score']:
                    set_clauses.append(f"{key} = ?")
                    values.append(value)
            
            if not set_clauses:
                return False
            
            set_clauses.append("updated_at = ?")
            values.append(datetime.utcnow().isoformat())
            
            values.append(work_id)
            
            await conn.execute(
                f"UPDATE works SET {', '.join(set_clauses)} WHERE id = ?",
                tuple(values)
            )
            await conn.commit()
            return True
        
        finally:
            await conn.close()
    
    @staticmethod
    async def delete(work_id: str) -> bool:
        """文献を削除"""
        conn = await get_async_connection()
        try:
            await conn.execute("DELETE FROM works WHERE id = ?", (work_id,))
            await conn.commit()
            return True
        finally:
            await conn.close()


class CheckDAO:
    """検証結果データアクセス"""
    
    @staticmethod
    async def create(
        work_id: str,
        kind: str,
        status: str,
        detail: str,
        http_code: Optional[int] = None
    ) -> int:
        """検証結果を作成"""
        conn = await get_async_connection()
        try:
            cursor = await conn.execute(
                """
                INSERT INTO checks (work_id, kind, status, detail, http_code)
                VALUES (?, ?, ?, ?, ?)
                """,
                (work_id, kind, status, detail, http_code)
            )
            await conn.commit()
            return cursor.lastrowid
        finally:
            await conn.close()
    
    @staticmethod
    async def get_by_work(work_id: str) -> List[Dict[str, Any]]:
        """文献の検証結果を取得"""
        conn = await get_async_connection()
        try:
            cursor = await conn.execute(
                "SELECT * FROM checks WHERE work_id = ? ORDER BY checked_at DESC",
                (work_id,)
            )
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]
        finally:
            await conn.close()


class ReadEvidenceDAO:
    """既読証跡データアクセス"""
    
    @staticmethod
    async def create(
        work_id: str,
        pdf_path: str,
        page: int,
        dwell_secs: int,
        coverage: float,
        snippet_hash: Optional[str] = None
    ) -> int:
        """既読証跡を作成"""
        conn = await get_async_connection()
        try:
            cursor = await conn.execute(
                """
                INSERT INTO read_evidence 
                (work_id, pdf_path, page, dwell_secs, coverage, snippet_hash)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (work_id, pdf_path, page, dwell_secs, coverage, snippet_hash)
            )
            await conn.commit()
            return cursor.lastrowid
        finally:
            await conn.close()
    
    @staticmethod
    async def get_by_work(work_id: str) -> List[Dict[str, Any]]:
        """文献の既読証跡を取得"""
        conn = await get_async_connection()
        try:
            cursor = await conn.execute(
                "SELECT * FROM read_evidence WHERE work_id = ? ORDER BY page, created_at",
                (work_id,)
            )
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]
        finally:
            await conn.close()


class ClaimCardDAO:
    """引用文脈カードデータアクセス"""
    
    @staticmethod
    async def create(
        card_id: str,
        work_id: str,
        claim: str,
        evidence_snippet: str,
        page_from: int,
        page_to: Optional[int] = None,
        limitations: Optional[str] = None,
        verified: bool = False
    ) -> str:
        """カードを作成"""
        conn = await get_async_connection()
        try:
            await conn.execute(
                """
                INSERT INTO claim_cards 
                (id, work_id, claim, evidence_snippet, page_from, page_to, 
                 limitations, verified)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (card_id, work_id, claim, evidence_snippet, page_from,
                 page_to, limitations, verified)
            )
            await conn.commit()
            return card_id
        finally:
            await conn.close()
    
    @staticmethod
    async def get(card_id: str) -> Optional[Dict[str, Any]]:
        """カードを取得"""
        conn = await get_async_connection()
        try:
            cursor = await conn.execute(
                "SELECT * FROM claim_cards WHERE id = ?",
                (card_id,)
            )
            row = await cursor.fetchone()
            return dict(row) if row else None
        finally:
            await conn.close()
    
    @staticmethod
    async def get_by_work(work_id: str) -> List[Dict[str, Any]]:
        """文献のカードを取得"""
        conn = await get_async_connection()
        try:
            cursor = await conn.execute(
                "SELECT * FROM claim_cards WHERE work_id = ? ORDER BY created_at",
                (work_id,)
            )
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]
        finally:
            await conn.close()
    
    @staticmethod
    async def update(card_id: str, updates: Dict[str, Any]) -> bool:
        """カードを更新"""
        conn = await get_async_connection()
        try:
            set_clauses = []
            values = []
            
            for key, value in updates.items():
                if key in ['claim', 'evidence_snippet', 'page_from', 'page_to', 
                          'limitations', 'verified']:
                    set_clauses.append(f"{key} = ?")
                    values.append(value)
            
            if not set_clauses:
                return False
            
            set_clauses.append("updated_at = ?")
            values.append(datetime.utcnow().isoformat())
            
            values.append(card_id)
            
            await conn.execute(
                f"UPDATE claim_cards SET {', '.join(set_clauses)} WHERE id = ?",
                tuple(values)
            )
            await conn.commit()
            return True
        finally:
            await conn.close()
    
    @staticmethod
    async def delete(card_id: str) -> bool:
        """カードを削除"""
        conn = await get_async_connection()
        try:
            await conn.execute("DELETE FROM claim_cards WHERE id = ?", (card_id,))
            await conn.commit()
            return True
        finally:
            await conn.close()


if __name__ == "__main__":
    import asyncio
    from refsys.models import CSLName, CSLDate
    
    async def test():
        # テスト文献作成
        test_csl = CSLItem(
            id="test_001",
            type="article-journal",
            title="Test Article",
            author=[CSLName(family="Doe", given="John")],
            issued=CSLDate(date_parts=[[2023]]),
            DOI="10.1234/test.001"
        )
        
        # 作成
        work_id = await WorkDAO.create(test_csl)
        print(f"Created work: {work_id}")
        
        # 取得
        work = await WorkDAO.get(work_id)
        print(f"Retrieved: {work['title']}")
        
        # リスト
        works = await WorkDAO.list_all()
        print(f"Total works: {len(works)}")
    
    asyncio.run(test())
