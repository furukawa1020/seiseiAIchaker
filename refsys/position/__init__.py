"""
文献の位置づけ判定: 査読有無、引用数、合意度スコア
"""
import re
from typing import Optional, Dict, Any, List
from datetime import datetime
import httpx


class PositionMetadata:
    """文献の位置づけメタデータ"""
    def __init__(
        self,
        peer_reviewed: Optional[bool] = None,
        citation_count: int = 0,
        is_review: bool = False,
        is_meta_analysis: bool = False,
        publication_type: str = "unknown",
        year: Optional[int] = None,
        consensus_score: int = 0
    ):
        self.peer_reviewed = peer_reviewed
        self.citation_count = citation_count
        self.is_review = is_review
        self.is_meta_analysis = is_meta_analysis
        self.publication_type = publication_type
        self.year = year
        self.consensus_score = consensus_score
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'peer_reviewed': self.peer_reviewed,
            'citation_count': self.citation_count,
            'is_review': self.is_review,
            'is_meta_analysis': self.is_meta_analysis,
            'publication_type': self.publication_type,
            'year': self.year,
            'consensus_score': self.consensus_score
        }


class PositionAnalyzer:
    """文献の位置づけ分析"""
    
    REVIEW_KEYWORDS = [
        'review', 'survey', 'systematic review', 'literature review',
        'meta-analysis', 'meta analysis', 'scoping review'
    ]
    
    PEER_REVIEWED_TYPES = {
        'article-journal',
        'paper-conference',
        'chapter'
    }
    
    NON_PEER_REVIEWED_TYPES = {
        'report',
        'post',
        'webpage',
        'manuscript'
    }
    
    def __init__(self, cache_manager=None):
        self.cache = cache_manager
    
    def analyze_publication_type(self, csl_type: str, container_title: Optional[str] = None) -> str:
        """出版物タイプの分析"""
        if csl_type in self.PEER_REVIEWED_TYPES:
            if 'conference' in csl_type or 'conference' in (container_title or '').lower():
                return 'conference'
            return 'journal'
        
        if csl_type == 'book' or csl_type == 'chapter':
            return 'book'
        
        if csl_type in self.NON_PEER_REVIEWED_TYPES:
            return 'non-peer-reviewed'
        
        # arXivなどのプレプリント判定
        if container_title:
            if 'arxiv' in container_title.lower():
                return 'preprint'
            if 'biorxiv' in container_title.lower() or 'medrxiv' in container_title.lower():
                return 'preprint'
        
        return 'unknown'
    
    def is_peer_reviewed(self, csl_type: str, container_title: Optional[str] = None) -> Optional[bool]:
        """査読の有無判定"""
        pub_type = self.analyze_publication_type(csl_type, container_title)
        
        if pub_type in ['journal', 'conference']:
            return True
        elif pub_type in ['preprint', 'non-peer-reviewed']:
            return False
        else:
            return None  # 不明
    
    def is_review_article(self, title: Optional[str], container_title: Optional[str] = None) -> bool:
        """レビュー論文か判定"""
        if not title:
            return False
        
        title_lower = title.lower()
        for keyword in self.REVIEW_KEYWORDS:
            if keyword in title_lower:
                return True
        
        # ジャーナル名にもチェック
        if container_title:
            container_lower = container_title.lower()
            if 'review' in container_lower:
                return True
        
        return False
    
    def is_meta_analysis(self, title: Optional[str], abstract: Optional[str] = None) -> bool:
        """メタ解析か判定"""
        if not title:
            return False
        
        text = title.lower()
        if abstract:
            text += ' ' + abstract.lower()
        
        return 'meta-analysis' in text or 'meta analysis' in text or 'metaanalysis' in text
    
    async def fetch_citation_count(
        self,
        doi: Optional[str] = None,
        title: Optional[str] = None
    ) -> int:
        """引用数の取得（OpenAlex API使用）"""
        if not doi and not title:
            return 0
        
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                if doi:
                    # DOIで検索
                    url = f"https://api.openalex.org/works/doi:{doi}"
                    response = await client.get(url)
                    
                    if response.status_code == 200:
                        data = response.json()
                        return data.get('cited_by_count', 0)
                
                if title:
                    # タイトルで検索
                    url = f"https://api.openalex.org/works?filter=title.search:{title}"
                    response = await client.get(url)
                    
                    if response.status_code == 200:
                        data = response.json()
                        results = data.get('results', [])
                        if results:
                            return results[0].get('cited_by_count', 0)
        except:
            pass
        
        return 0
    
    def calculate_consensus_score(
        self,
        citation_count: int,
        is_peer_reviewed: Optional[bool],
        is_review: bool,
        is_meta_analysis: bool,
        year: Optional[int],
        is_retracted: bool = False
    ) -> int:
        """合意度スコアの計算（0-100）"""
        score = 50  # ベーススコア
        
        # 引用数による加点（対数スケール）
        if citation_count > 0:
            import math
            citation_bonus = min(30, int(10 * math.log10(citation_count + 1)))
            score += citation_bonus
        
        # 査読による加点
        if is_peer_reviewed is True:
            score += 10
        elif is_peer_reviewed is False:
            score -= 10
        
        # レビュー論文/メタ解析による加点
        if is_meta_analysis:
            score += 15
        elif is_review:
            score += 10
        
        # 年代による調整
        if year:
            current_year = datetime.now().year
            age = current_year - year
            
            if age < 0:
                # 未来の年（エラー）
                score -= 20
            elif age <= 2:
                # 新しすぎる（まだ検証が不十分の可能性）
                score -= 5
            elif age <= 5:
                # 適度に新しい
                score += 5
            elif age <= 10:
                # やや古い
                pass
            else:
                # 古い（再確認推奨）
                score -= min(10, (age - 10) // 5)
        
        # リトラクション（撤回）による大幅減点
        if is_retracted:
            score -= 50
        
        # スコアを0-100に収める
        return max(0, min(100, score))
    
    async def analyze_work(self, work_data: Dict[str, Any]) -> PositionMetadata:
        """文献の完全分析"""
        csl_type = work_data.get('type', 'unknown')
        container_title = work_data.get('container-title') or work_data.get('container_title')
        title = work_data.get('title')
        doi = work_data.get('DOI')
        year = None
        
        # 年の取得
        if 'issued' in work_data:
            issued = work_data['issued']
            if isinstance(issued, dict) and 'date-parts' in issued:
                date_parts = issued['date-parts']
                if date_parts and len(date_parts) > 0 and len(date_parts[0]) > 0:
                    year = date_parts[0][0]
        
        # 査読判定
        peer_reviewed = self.is_peer_reviewed(csl_type, container_title)
        
        # レビュー/メタ解析判定
        is_review = self.is_review_article(title, container_title)
        is_meta = self.is_meta_analysis(title, work_data.get('abstract'))
        
        # 引用数取得
        citation_count = await self.fetch_citation_count(doi, title)
        
        # 出版タイプ
        pub_type = self.analyze_publication_type(csl_type, container_title)
        
        # リトラクション
        is_retracted = work_data.get('retracted', False)
        
        # 合意度スコア計算
        consensus_score = self.calculate_consensus_score(
            citation_count=citation_count,
            is_peer_reviewed=peer_reviewed,
            is_review=is_review,
            is_meta_analysis=is_meta,
            year=year,
            is_retracted=is_retracted
        )
        
        return PositionMetadata(
            peer_reviewed=peer_reviewed,
            citation_count=citation_count,
            is_review=is_review,
            is_meta_analysis=is_meta,
            publication_type=pub_type,
            year=year,
            consensus_score=consensus_score
        )


def get_consensus_label(score: int) -> str:
    """合意度スコアのラベル"""
    if score >= 80:
        return "非常に高い"
    elif score >= 65:
        return "高い"
    elif score >= 50:
        return "中程度"
    elif score >= 35:
        return "やや低い"
    else:
        return "低い"


def format_position_summary(metadata: PositionMetadata) -> str:
    """位置づけサマリーのフォーマット"""
    lines = []
    
    # 査読
    if metadata.peer_reviewed is True:
        lines.append("✅ 査読あり")
    elif metadata.peer_reviewed is False:
        lines.append("⚠️ 査読なし")
    else:
        lines.append("❓ 査読不明")
    
    # タイプ
    lines.append(f"📄 タイプ: {metadata.publication_type}")
    
    # 引用数
    lines.append(f"📊 引用数: {metadata.citation_count}")
    
    # レビュー/メタ解析
    if metadata.is_meta_analysis:
        lines.append("📖 メタ解析")
    elif metadata.is_review:
        lines.append("📖 レビュー論文")
    
    # 年
    if metadata.year:
        lines.append(f"📅 発行年: {metadata.year}")
    
    # 合意度スコア
    label = get_consensus_label(metadata.consensus_score)
    lines.append(f"🎯 合意度（目安）: {metadata.consensus_score}/100 ({label})")
    lines.append("    ※これは参考値であり、断定的な評価ではありません")
    
    return "\n".join(lines)


if __name__ == "__main__":
    # テスト
    import asyncio
    
    async def test():
        analyzer = PositionAnalyzer()
        
        work_data = {
            'type': 'article-journal',
            'title': 'A systematic review of machine learning',
            'container-title': 'Nature Reviews',
            'DOI': '10.1038/s41586-021-03819-2',
            'issued': {'date-parts': [[2021]]},
            'retracted': False
        }
        
        metadata = await analyzer.analyze_work(work_data)
        print(format_position_summary(metadata))
    
    asyncio.run(test())
