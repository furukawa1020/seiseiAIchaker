"""
参考文献のフォーマット: APA7 / IEEE
"""
import re
from typing import List, Dict, Any, Optional
from refsys.models import CSLItem, CSLName


class ReferenceFormatter:
    """参考文献フォーマッタ"""
    
    def __init__(self, style: str = "apa"):
        """
        Args:
            style: "apa" or "ieee"
        """
        self.style = style.lower()
        if self.style not in ["apa", "ieee"]:
            raise ValueError(f"Unsupported style: {style}. Use 'apa' or 'ieee'.")
    
    def format_authors(self, authors: List[CSLName]) -> str:
        """著者のフォーマット"""
        if not authors:
            return ""
        
        if self.style == "apa":
            return self._format_authors_apa(authors)
        elif self.style == "ieee":
            return self._format_authors_ieee(authors)
    
    def _format_authors_apa(self, authors: List[CSLName]) -> str:
        """APA形式の著者（Family, G.）"""
        formatted = []
        
        for i, author in enumerate(authors[:20]):  # 最大20名
            if author.literal:
                formatted.append(author.literal)
            else:
                parts = []
                if author.family:
                    parts.append(author.family)
                if author.given:
                    # イニシャル化
                    initials = ''.join([name[0] + '.' for name in author.given.split()])
                    parts.append(initials)
                formatted.append(', '.join(parts))
        
        if len(authors) > 20:
            formatted.append("... " + self._format_single_author_apa(authors[-1]))
        
        if len(formatted) == 1:
            return formatted[0]
        elif len(formatted) == 2:
            return f"{formatted[0]}, & {formatted[1]}"
        else:
            return ', '.join(formatted[:-1]) + f", & {formatted[-1]}"
    
    def _format_single_author_apa(self, author: CSLName) -> str:
        """APA形式の単一著者"""
        if author.literal:
            return author.literal
        
        parts = []
        if author.family:
            parts.append(author.family)
        if author.given:
            initials = ''.join([name[0] + '.' for name in author.given.split()])
            parts.append(initials)
        return ', '.join(parts)
    
    def _format_authors_ieee(self, authors: List[CSLName]) -> str:
        """IEEE形式の著者（G. Family）"""
        formatted = []
        
        for author in authors[:6]:  # 最大6名
            if author.literal:
                formatted.append(author.literal)
            else:
                parts = []
                if author.given:
                    initials = '. '.join([name[0] for name in author.given.split()]) + '.'
                    parts.append(initials)
                if author.family:
                    parts.append(author.family)
                formatted.append(' '.join(parts))
        
        if len(authors) > 6:
            formatted.append("et al.")
        
        return ', '.join(formatted)
    
    def format_reference(self, csl: CSLItem) -> str:
        """参考文献のフォーマット"""
        if self.style == "apa":
            return self._format_apa(csl)
        elif self.style == "ieee":
            return self._format_ieee(csl)
    
    def _format_apa(self, csl: CSLItem) -> str:
        """APA7形式"""
        parts = []
        
        # 著者
        if csl.author:
            parts.append(self.format_authors(csl.author))
        
        # 年
        year = csl.issued.get_year() if csl.issued else None
        if year:
            parts.append(f"({year})")
        else:
            parts.append("(n.d.)")
        
        # タイトル
        if csl.title:
            # 記事・論文はイタリックなし、書籍はイタリック
            if csl.type in ['book', 'report']:
                parts.append(f"*{csl.title}*")
            else:
                parts.append(csl.title)
        
        # コンテナ（ジャーナル名など）
        if csl.container_title:
            container_parts = [f"*{csl.container_title}*"]
            
            # 巻・号
            if csl.volume:
                vol_str = f"*{csl.volume}*"
                if csl.issue:
                    vol_str += f"({csl.issue})"
                container_parts.append(vol_str)
            
            # ページ
            if csl.page:
                container_parts.append(csl.page)
            
            parts.append(', '.join(container_parts))
        
        # DOI or URL
        if csl.DOI:
            parts.append(f"https://doi.org/{csl.DOI}")
        elif csl.URL:
            parts.append(csl.URL)
        
        return '. '.join(parts) + '.'
    
    def _format_ieee(self, csl: CSLItem) -> str:
        """IEEE形式"""
        parts = []
        
        # 著者
        if csl.author:
            authors = self.format_authors(csl.author)
            parts.append(authors + ',')
        
        # タイトル
        if csl.title:
            if csl.type in ['book', 'report']:
                parts.append(f"*{csl.title}*.")
            else:
                parts.append(f'"{csl.title},"')
        
        # コンテナ
        if csl.container_title:
            parts.append(f"*{csl.container_title}*,")
            
            if csl.volume:
                parts.append(f"vol. {csl.volume},")
            
            if csl.issue:
                parts.append(f"no. {csl.issue},")
            
            if csl.page:
                parts.append(f"pp. {csl.page},")
        
        # 年
        year = csl.issued.get_year() if csl.issued else None
        if year:
            parts.append(f"{year}.")
        
        # DOI or URL
        if csl.DOI:
            parts.append(f"doi: {csl.DOI}")
        elif csl.URL:
            parts.append(f"[Online]. Available: {csl.URL}")
        
        return ' '.join(parts)
    
    def format_bibliography(self, items: List[CSLItem], sort: bool = True) -> str:
        """参考文献リスト全体のフォーマット"""
        if sort:
            # APA: アルファベット順、IEEE: 出現順（引用番号順）
            if self.style == "apa":
                items = sorted(
                    items,
                    key=lambda x: (
                        x.author[0].family.lower() if x.author and x.author[0].family else '',
                        x.issued.get_year() if x.issued else 9999
                    )
                )
        
        lines = []
        for i, item in enumerate(items, 1):
            ref = self.format_reference(item)
            
            if self.style == "ieee":
                lines.append(f"[{i}] {ref}")
            else:
                lines.append(ref)
        
        return '\n\n'.join(lines)


class InTextCitation:
    """本文中引用"""
    
    def __init__(self, style: str = "apa"):
        self.style = style.lower()
    
    def cite(self, csl: CSLItem, page: Optional[str] = None) -> str:
        """本文中引用の生成"""
        if self.style == "apa":
            return self._cite_apa(csl, page)
        elif self.style == "ieee":
            return self._cite_ieee(csl)
    
    def _cite_apa(self, csl: CSLItem, page: Optional[str] = None) -> str:
        """APA形式の本文中引用（著者-年）"""
        if not csl.author:
            author_part = "Unknown"
        elif len(csl.author) == 1:
            author_part = csl.author[0].family or "Unknown"
        elif len(csl.author) == 2:
            author_part = f"{csl.author[0].family} & {csl.author[1].family}"
        else:
            author_part = f"{csl.author[0].family} et al."
        
        year = csl.issued.get_year() if csl.issued else "n.d."
        
        if page:
            return f"({author_part}, {year}, p. {page})"
        else:
            return f"({author_part}, {year})"
    
    def _cite_ieee(self, csl: CSLItem, number: Optional[int] = None) -> str:
        """IEEE形式の本文中引用（番号）"""
        if number:
            return f"[{number}]"
        else:
            return "[?]"


def export_to_bibtex(items: List[CSLItem]) -> str:
    """BibTeX形式でエクスポート"""
    entries = []
    
    for item in items:
        entry_type = _map_csl_type_to_bibtex(item.type)
        cite_key = item.id
        
        fields = []
        
        # 著者
        if item.author:
            authors = ' and '.join([
                f"{a.family}, {a.given}" if a.family and a.given else (a.family or a.given or a.literal or "")
                for a in item.author
            ])
            fields.append(f"  author = {{{authors}}}")
        
        # タイトル
        if item.title:
            fields.append(f"  title = {{{item.title}}}")
        
        # ジャーナル/ブック
        if item.container_title:
            if item.type == 'article-journal':
                fields.append(f"  journal = {{{item.container_title}}}")
            elif item.type == 'book':
                fields.append(f"  booktitle = {{{item.container_title}}}")
        
        # 年
        if item.issued:
            year = item.issued.get_year()
            if year:
                fields.append(f"  year = {{{year}}}")
        
        # 巻・号・ページ
        if item.volume:
            fields.append(f"  volume = {{{item.volume}}}")
        if item.issue:
            fields.append(f"  number = {{{item.issue}}}")
        if item.page:
            fields.append(f"  pages = {{{item.page}}}")
        
        # DOI
        if item.DOI:
            fields.append(f"  doi = {{{item.DOI}}}")
        
        # URL
        if item.URL:
            fields.append(f"  url = {{{item.URL}}}")
        
        entry = f"@{entry_type}{{{cite_key},\n" + ',\n'.join(fields) + "\n}"
        entries.append(entry)
    
    return '\n\n'.join(entries)


def _map_csl_type_to_bibtex(csl_type: str) -> str:
    """CSLタイプをBibTeXタイプにマップ"""
    mapping = {
        'article-journal': 'article',
        'paper-conference': 'inproceedings',
        'chapter': 'inbook',
        'book': 'book',
        'report': 'techreport',
        'thesis': 'phdthesis',
        'manuscript': 'unpublished'
    }
    return mapping.get(csl_type, 'misc')


if __name__ == "__main__":
    # テスト
    from refsys.models import CSLName, CSLDate
    
    test_item = CSLItem(
        id="lazarus1984",
        type="article-journal",
        title="On the relationship between emotion and cognition",
        author=[CSLName(family="Lazarus", given="Richard S.")],
        issued=CSLDate(date_parts=[[1984]]),
        container_title="American Psychologist",
        volume="39",
        issue="2",
        page="124-129",
        DOI="10.1037/0003-066X.39.2.124"
    )
    
    # APA形式
    apa_formatter = ReferenceFormatter("apa")
    print("=== APA7 ===")
    print(apa_formatter.format_reference(test_item))
    print()
    
    # IEEE形式
    ieee_formatter = ReferenceFormatter("ieee")
    print("=== IEEE ===")
    print(ieee_formatter.format_reference(test_item))
    print()
    
    # 本文中引用
    apa_cite = InTextCitation("apa")
    print("=== In-text (APA) ===")
    print(apa_cite.cite(test_item, page="125"))
