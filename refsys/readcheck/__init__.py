"""
既読検証: PDF閲覧ログ、ハイライト、引用文脈カード
"""
import hashlib
import re
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path
from datetime import datetime
import json


class ReadingEvidence:
    """読書証跡"""
    def __init__(
        self,
        work_id: str,
        pdf_path: str,
        page: int,
        dwell_secs: int = 0,
        coverage: float = 0.0,
        snippet: Optional[str] = None
    ):
        self.work_id = work_id
        self.pdf_path = pdf_path
        self.page = page
        self.dwell_secs = dwell_secs
        self.coverage = coverage
        self.snippet_hash = self._hash_snippet(snippet) if snippet else None
        self.created_at = datetime.utcnow()
    
    def _hash_snippet(self, snippet: str) -> str:
        """スニペットのハッシュ化（著作権配慮）"""
        return hashlib.sha256(snippet.encode()).hexdigest()
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'work_id': self.work_id,
            'pdf_path': self.pdf_path,
            'page': self.page,
            'dwell_secs': self.dwell_secs,
            'coverage': self.coverage,
            'snippet_hash': self.snippet_hash,
            'created_at': self.created_at.isoformat()
        }


class ClaimCard:
    """引用文脈カード"""
    def __init__(
        self,
        work_id: str,
        claim: str,
        evidence_snippet: str,
        page_from: int,
        page_to: Optional[int] = None,
        limitations: Optional[str] = None,
        verified: bool = False,
        card_id: Optional[str] = None
    ):
        self.id = card_id or self._generate_id()
        self.work_id = work_id
        self.claim = claim
        self.evidence_snippet = evidence_snippet
        self.page_from = page_from
        self.page_to = page_to or page_from
        self.limitations = limitations
        self.verified = verified
        self.created_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
    
    def _generate_id(self) -> str:
        """カードIDの生成"""
        import uuid
        return f"card_{uuid.uuid4().hex[:12]}"
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'work_id': self.work_id,
            'claim': self.claim,
            'evidence_snippet': self.evidence_snippet,
            'page_from': self.page_from,
            'page_to': self.page_to,
            'limitations': self.limitations,
            'verified': self.verified,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
    
    def is_complete(self) -> bool:
        """カードが完成しているか"""
        return bool(
            self.claim and
            self.evidence_snippet and
            self.page_from and
            len(self.evidence_snippet) >= 20  # 最低20文字
        )


class PDFReader:
    """PDF読み取り・抽出"""
    def __init__(self, pdf_path: str):
        self.pdf_path = Path(pdf_path)
        if not self.pdf_path.exists():
            raise FileNotFoundError(f"PDF not found: {pdf_path}")
    
    def extract_text(self, page_num: Optional[int] = None) -> str:
        """テキスト抽出"""
        try:
            import fitz  # PyMuPDF
            doc = fitz.open(str(self.pdf_path))
            
            if page_num is not None:
                if 0 <= page_num < len(doc):
                    text = doc[page_num].get_text()
                    doc.close()
                    return text
                else:
                    doc.close()
                    return ""
            else:
                # 全ページ
                texts = []
                for page in doc:
                    texts.append(page.get_text())
                doc.close()
                return "\n\n".join(texts)
        
        except ImportError:
            # pdfminerにフォールバック
            from pdfminer.high_level import extract_text
            return extract_text(str(self.pdf_path))
    
    def get_page_count(self) -> int:
        """ページ数取得"""
        try:
            import fitz
            doc = fitz.open(str(self.pdf_path))
            count = len(doc)
            doc.close()
            return count
        except ImportError:
            from pdfminer.pdfparser import PDFParser
            from pdfminer.pdfdocument import PDFDocument
            
            with open(str(self.pdf_path), 'rb') as f:
                parser = PDFParser(f)
                doc = PDFDocument(parser)
                return doc.catalog.get('Pages', {}).get('Count', 0)
    
    def extract_page_range(self, start: int, end: int) -> Dict[int, str]:
        """ページ範囲のテキスト抽出"""
        result = {}
        for page_num in range(start, end + 1):
            text = self.extract_text(page_num)
            if text:
                result[page_num] = text
        return result
    
    def search_text(self, query: str, case_sensitive: bool = False) -> List[Tuple[int, str]]:
        """テキスト検索（ページ番号と周辺テキストを返す）"""
        matches = []
        try:
            import fitz
            doc = fitz.open(str(self.pdf_path))
            
            for page_num, page in enumerate(doc):
                text = page.get_text()
                if case_sensitive:
                    if query in text:
                        # 周辺テキストを抽出
                        idx = text.index(query)
                        context_start = max(0, idx - 50)
                        context_end = min(len(text), idx + len(query) + 50)
                        context = text[context_start:context_end]
                        matches.append((page_num, context))
                else:
                    if query.lower() in text.lower():
                        idx = text.lower().index(query.lower())
                        context_start = max(0, idx - 50)
                        context_end = min(len(text), idx + len(query) + 50)
                        context = text[context_start:context_end]
                        matches.append((page_num, context))
            
            doc.close()
        except:
            pass
        
        return matches


class ReadingScorer:
    """既読スコア計算"""
    def __init__(
        self,
        min_dwell_secs: int = 20,
        min_coverage: float = 0.9,
        min_pages_read: float = 0.8
    ):
        self.min_dwell_secs = min_dwell_secs
        self.min_coverage = min_coverage
        self.min_pages_read = min_pages_read
    
    def calculate_score(
        self,
        evidences: List[ReadingEvidence],
        total_pages: int,
        cards: List[ClaimCard]
    ) -> Dict[str, Any]:
        """既読スコアの計算"""
        if total_pages == 0:
            return {
                'score': 0,
                'passed': False,
                'details': 'No pages in document'
            }
        
        # ページごとの滞在時間と到達率
        page_stats = {}
        for evidence in evidences:
            if evidence.page not in page_stats:
                page_stats[evidence.page] = {
                    'dwell_secs': 0,
                    'max_coverage': 0.0
                }
            page_stats[evidence.page]['dwell_secs'] += evidence.dwell_secs
            page_stats[evidence.page]['max_coverage'] = max(
                page_stats[evidence.page]['max_coverage'],
                evidence.coverage
            )
        
        # 条件を満たすページ数
        qualified_pages = 0
        for page, stats in page_stats.items():
            if (stats['dwell_secs'] >= self.min_dwell_secs and
                stats['max_coverage'] >= self.min_coverage):
                qualified_pages += 1
        
        # 読了率
        read_ratio = qualified_pages / total_pages if total_pages > 0 else 0
        
        # カード完成度
        complete_cards = sum(1 for card in cards if card.is_complete())
        card_score = min(1.0, complete_cards / max(1, len(cards))) if cards else 0
        
        # 総合スコア（0-100）
        score = int((read_ratio * 0.6 + card_score * 0.4) * 100)
        
        # 合格判定
        passed = (
            read_ratio >= self.min_pages_read and
            complete_cards > 0
        )
        
        return {
            'score': score,
            'passed': passed,
            'read_ratio': read_ratio,
            'qualified_pages': qualified_pages,
            'total_pages': total_pages,
            'complete_cards': complete_cards,
            'total_cards': len(cards),
            'details': self._generate_details(
                read_ratio, qualified_pages, total_pages,
                complete_cards, len(cards), passed
            )
        }
    
    def _generate_details(
        self,
        read_ratio: float,
        qualified_pages: int,
        total_pages: int,
        complete_cards: int,
        total_cards: int,
        passed: bool
    ) -> str:
        """詳細メッセージ生成"""
        parts = [
            f"読了ページ: {qualified_pages}/{total_pages} ({read_ratio*100:.1f}%)",
            f"完成カード: {complete_cards}/{total_cards if total_cards > 0 else 0}"
        ]
        
        if passed:
            parts.append("✅ 既読検証: PASS")
        else:
            parts.append("❌ 既読検証: 要追加作業")
            if read_ratio < self.min_pages_read:
                parts.append(f"  - さらに {int((self.min_pages_read - read_ratio) * total_pages)} ページの読了が必要")
            if complete_cards == 0:
                parts.append("  - 引用文脈カードの作成が必要")
        
        return "\n".join(parts)


class QuizGenerator:
    """理解確認クイズ生成"""
    def __init__(self):
        pass
    
    def extract_keywords(self, text: str, top_n: int = 10) -> List[str]:
        """キーワード抽出（簡易TF）"""
        # ストップワード（簡易版）
        stopwords = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
            'of', 'with', 'by', 'from', 'as', 'is', 'was', 'are', 'were', 'be',
            'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will',
            'would', 'should', 'could', 'can', 'may', 'might', 'must', 'that',
            'this', 'these', 'those', 'i', 'you', 'he', 'she', 'it', 'we', 'they'
        }
        
        # 単語抽出と頻度カウント
        words = re.findall(r'\b[a-zA-Z]{4,}\b', text.lower())
        word_freq = {}
        for word in words:
            if word not in stopwords:
                word_freq[word] = word_freq.get(word, 0) + 1
        
        # 頻度順にソート
        sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
        return [word for word, freq in sorted_words[:top_n]]
    
    def generate_cloze_questions(
        self,
        text: str,
        num_questions: int = 5
    ) -> List[Dict[str, str]]:
        """穴埋め問題生成"""
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if len(s.strip()) > 30]
        
        if len(sentences) < num_questions:
            num_questions = len(sentences)
        
        # キーワードを含む文を選択
        keywords = self.extract_keywords(text, top_n=20)
        
        questions = []
        used_sentences = set()
        
        for keyword in keywords:
            if len(questions) >= num_questions:
                break
            
            for i, sentence in enumerate(sentences):
                if i in used_sentences:
                    continue
                
                if keyword in sentence.lower():
                    # キーワードを穴埋めに
                    pattern = re.compile(r'\b' + re.escape(keyword) + r'\b', re.IGNORECASE)
                    match = pattern.search(sentence)
                    if match:
                        question_text = pattern.sub('_____', sentence, count=1)
                        questions.append({
                            'question': question_text,
                            'answer': match.group(),
                            'type': 'cloze'
                        })
                        used_sentences.add(i)
                        break
        
        return questions[:num_questions]


def create_reading_session(
    work_id: str,
    pdf_path: str
) -> Dict[str, Any]:
    """読書セッション作成"""
    reader = PDFReader(pdf_path)
    page_count = reader.get_page_count()
    
    return {
        'work_id': work_id,
        'pdf_path': str(pdf_path),
        'page_count': page_count,
        'started_at': datetime.utcnow().isoformat(),
        'evidences': [],
        'cards': []
    }


if __name__ == "__main__":
    # テスト
    test_text = """
    This is a sample academic text about machine learning.
    Machine learning is a subset of artificial intelligence.
    The algorithm learns patterns from data without explicit programming.
    Deep learning uses neural networks with multiple layers.
    """
    
    quiz_gen = QuizGenerator()
    keywords = quiz_gen.extract_keywords(test_text)
    print("Keywords:", keywords)
    
    questions = quiz_gen.generate_cloze_questions(test_text, num_questions=2)
    for q in questions:
        print(f"Q: {q['question']}")
        print(f"A: {q['answer']}\n")
