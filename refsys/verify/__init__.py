"""
文献の実在性検証・到達性チェック
"""
import re
import asyncio
import httpx
from typing import Optional, Dict, Any, List, Tuple
from datetime import datetime, timedelta
import hashlib
import json
from pathlib import Path


class VerificationResult:
    """検証結果"""
    def __init__(
        self,
        kind: str,
        status: str,  # 'ok', 'warn', 'fail'
        detail: str,
        http_code: Optional[int] = None,
        alternative_urls: Optional[List[str]] = None
    ):
        self.kind = kind
        self.status = status
        self.detail = detail
        self.http_code = http_code
        self.alternative_urls = alternative_urls or []
        self.checked_at = datetime.utcnow().isoformat()
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "kind": self.kind,
            "status": self.status,
            "detail": self.detail,
            "http_code": self.http_code,
            "alternative_urls": self.alternative_urls,
            "checked_at": self.checked_at
        }


class CacheManager:
    """APIレスポンスキャッシュ管理"""
    def __init__(self, cache_dir: Optional[Path] = None):
        self.cache_dir = cache_dir or Path.home() / ".refsys" / "cache"
        self.cache_dir.mkdir(parents=True, exist_ok=True)
    
    def _get_cache_path(self, key: str) -> Path:
        """キャッシュファイルパスを取得"""
        key_hash = hashlib.md5(key.encode()).hexdigest()
        return self.cache_dir / f"{key_hash}.json"
    
    def get(self, key: str) -> Optional[Dict[str, Any]]:
        """キャッシュから取得"""
        cache_path = self._get_cache_path(key)
        if not cache_path.exists():
            return None
        
        try:
            with open(cache_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # 有効期限チェック
            if 'expires_at' in data:
                expires_at = datetime.fromisoformat(data['expires_at'])
                if datetime.utcnow() > expires_at:
                    cache_path.unlink()
                    return None
            
            return data.get('value')
        except:
            return None
    
    def set(
        self,
        key: str,
        value: Any,
        ttl_hours: int = 24,
        etag: Optional[str] = None
    ):
        """キャッシュに保存"""
        cache_path = self._get_cache_path(key)
        
        data = {
            'value': value,
            'cached_at': datetime.utcnow().isoformat(),
            'expires_at': (datetime.utcnow() + timedelta(hours=ttl_hours)).isoformat(),
            'etag': etag
        }
        
        with open(cache_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)


class Verifier:
    """文献検証器"""
    def __init__(self, cache_manager: Optional[CacheManager] = None):
        self.cache = cache_manager or CacheManager()
        self.client = None
    
    async def __aenter__(self):
        self.client = httpx.AsyncClient(
            timeout=httpx.Timeout(30.0),
            follow_redirects=True,
            limits=httpx.Limits(max_keepalive_connections=5, max_connections=10)
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.client:
            await self.client.aclose()
    
    async def verify_doi(self, doi: str) -> VerificationResult:
        """DOIの検証"""
        # 形式チェック
        if not re.match(r'^10\.\d{4,9}/[-._;()/:A-Z0-9]+$', doi, re.IGNORECASE):
            return VerificationResult(
                kind='doi',
                status='fail',
                detail=f'Invalid DOI format: {doi}'
            )
        
        # キャッシュチェック
        cache_key = f"doi:{doi}"
        cached = self.cache.get(cache_key)
        if cached:
            return VerificationResult(**cached)
        
        # DOI.orgへのリクエスト
        url = f"https://doi.org/{doi}"
        try:
            response = await self.client.head(url, timeout=10.0)
            
            if response.status_code in [200, 301, 302, 303]:
                result = VerificationResult(
                    kind='doi',
                    status='ok',
                    detail=f'DOI resolves to {response.headers.get("location", url)}',
                    http_code=response.status_code
                )
            elif response.status_code == 404:
                result = VerificationResult(
                    kind='doi',
                    status='fail',
                    detail=f'DOI not found (404)',
                    http_code=404
                )
            else:
                result = VerificationResult(
                    kind='doi',
                    status='warn',
                    detail=f'Unexpected status code: {response.status_code}',
                    http_code=response.status_code
                )
            
            # キャッシュに保存
            self.cache.set(cache_key, result.to_dict(), ttl_hours=168)  # 1週間
            return result
        
        except httpx.TimeoutException:
            return VerificationResult(
                kind='doi',
                status='warn',
                detail='Request timeout'
            )
        except Exception as e:
            return VerificationResult(
                kind='doi',
                status='warn',
                detail=f'Error: {str(e)}'
            )
    
    async def verify_url(self, url: str) -> VerificationResult:
        """URLの到達性確認"""
        cache_key = f"url:{url}"
        cached = self.cache.get(cache_key)
        if cached:
            return VerificationResult(**cached)
        
        try:
            # HEADリクエスト
            response = await self.client.head(url, timeout=10.0)
            
            if response.status_code == 200:
                result = VerificationResult(
                    kind='url',
                    status='ok',
                    detail='URL is accessible',
                    http_code=200
                )
            elif response.status_code in [301, 302, 303, 307, 308]:
                redirect_url = response.headers.get('location', '')
                result = VerificationResult(
                    kind='url',
                    status='ok',
                    detail=f'Redirects to {redirect_url}',
                    http_code=response.status_code,
                    alternative_urls=[redirect_url] if redirect_url else []
                )
            elif response.status_code in [404, 410]:
                result = VerificationResult(
                    kind='url',
                    status='fail',
                    detail=f'URL not found ({response.status_code})',
                    http_code=response.status_code
                )
            else:
                result = VerificationResult(
                    kind='url',
                    status='warn',
                    detail=f'Unexpected status: {response.status_code}',
                    http_code=response.status_code
                )
            
            self.cache.set(cache_key, result.to_dict(), ttl_hours=24)
            return result
        
        except httpx.TimeoutException:
            return VerificationResult(
                kind='url',
                status='warn',
                detail='Request timeout'
            )
        except Exception as e:
            return VerificationResult(
                kind='url',
                status='warn',
                detail=f'Error: {str(e)}'
            )
    
    async def verify_arxiv(self, arxiv_id: str) -> VerificationResult:
        """arXiv IDの検証"""
        # 形式チェック
        if not (re.match(r'^\d{4}\.\d{4,5}(v\d+)?$', arxiv_id) or 
                re.match(r'^[a-z-]+/\d{7}$', arxiv_id, re.IGNORECASE)):
            return VerificationResult(
                kind='arxiv',
                status='fail',
                detail=f'Invalid arXiv ID format: {arxiv_id}'
            )
        
        cache_key = f"arxiv:{arxiv_id}"
        cached = self.cache.get(cache_key)
        if cached:
            return VerificationResult(**cached)
        
        # arXiv APIで確認
        api_url = f"http://export.arxiv.org/api/query?id_list={arxiv_id}"
        try:
            response = await self.client.get(api_url, timeout=10.0)
            
            if response.status_code == 200 and '<entry>' in response.text:
                result = VerificationResult(
                    kind='arxiv',
                    status='ok',
                    detail='arXiv ID verified',
                    http_code=200
                )
            else:
                result = VerificationResult(
                    kind='arxiv',
                    status='fail',
                    detail='arXiv ID not found',
                    http_code=response.status_code
                )
            
            self.cache.set(cache_key, result.to_dict(), ttl_hours=168)
            return result
        
        except Exception as e:
            return VerificationResult(
                kind='arxiv',
                status='warn',
                detail=f'Error: {str(e)}'
            )
    
    async def verify_pubmed(self, pubmed_id: str) -> VerificationResult:
        """PubMed IDの検証"""
        if not re.match(r'^\d+$', pubmed_id):
            return VerificationResult(
                kind='pubmed',
                status='fail',
                detail=f'Invalid PubMed ID format: {pubmed_id}'
            )
        
        cache_key = f"pubmed:{pubmed_id}"
        cached = self.cache.get(cache_key)
        if cached:
            return VerificationResult(**cached)
        
        # PubMed E-utilitiesで確認
        api_url = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?db=pubmed&id={pubmed_id}&retmode=json"
        try:
            response = await self.client.get(api_url, timeout=10.0)
            
            if response.status_code == 200:
                data = response.json()
                if 'result' in data and pubmed_id in data['result']:
                    result = VerificationResult(
                        kind='pubmed',
                        status='ok',
                        detail='PubMed ID verified',
                        http_code=200
                    )
                else:
                    result = VerificationResult(
                        kind='pubmed',
                        status='fail',
                        detail='PubMed ID not found'
                    )
            else:
                result = VerificationResult(
                    kind='pubmed',
                    status='warn',
                    detail=f'API error: {response.status_code}',
                    http_code=response.status_code
                )
            
            self.cache.set(cache_key, result.to_dict(), ttl_hours=168)
            return result
        
        except Exception as e:
            return VerificationResult(
                kind='pubmed',
                status='warn',
                detail=f'Error: {str(e)}'
            )
    
    async def check_retraction(self, doi: Optional[str] = None) -> VerificationResult:
        """リトラクション（撤回）チェック"""
        if not doi:
            return VerificationResult(
                kind='retraction',
                status='ok',
                detail='No DOI provided, skipping retraction check'
            )
        
        cache_key = f"retraction:{doi}"
        cached = self.cache.get(cache_key)
        if cached:
            return VerificationResult(**cached)
        
        # Crossref APIでrelationをチェック
        api_url = f"https://api.crossref.org/works/{doi}"
        try:
            response = await self.client.get(api_url, timeout=10.0)
            
            if response.status_code == 200:
                data = response.json()
                message = data.get('message', {})
                
                # リトラクション関連のrelationをチェック
                relations = message.get('relation', {})
                is_retracted = False
                retraction_info = []
                
                for rel_type in ['is-correction-of', 'is-retracted-by', 'has-correction']:
                    if rel_type in relations:
                        is_retracted = True
                        retraction_info.append(rel_type)
                
                if is_retracted:
                    result = VerificationResult(
                        kind='retraction',
                        status='fail',
                        detail=f'⚠️ RETRACTED or CORRECTED: {", ".join(retraction_info)}'
                    )
                else:
                    result = VerificationResult(
                        kind='retraction',
                        status='ok',
                        detail='No retraction found'
                    )
            else:
                result = VerificationResult(
                    kind='retraction',
                    status='warn',
                    detail='Could not check retraction status'
                )
            
            self.cache.set(cache_key, result.to_dict(), ttl_hours=168)
            return result
        
        except Exception as e:
            return VerificationResult(
                kind='retraction',
                status='warn',
                detail=f'Error: {str(e)}'
            )
    
    async def find_alternative_urls(self, doi: str, title: Optional[str] = None) -> List[str]:
        """死リンク時の代替URL探索"""
        alternatives = []
        
        # Unpaywall API（OA版）
        try:
            email = "refsys@localhost"  # 実際は設定から取得
            api_url = f"https://api.unpaywall.org/v2/{doi}?email={email}"
            response = await self.client.get(api_url, timeout=10.0)
            
            if response.status_code == 200:
                data = response.json()
                
                # OAロケーション
                if data.get('is_oa'):
                    oa_url = data.get('best_oa_location', {}).get('url')
                    if oa_url:
                        alternatives.append(oa_url)
                
                # 出版社URL
                publisher_url = data.get('doi_url')
                if publisher_url:
                    alternatives.append(publisher_url)
        except:
            pass
        
        return alternatives


async def verify_work(
    work_data: Dict[str, Any],
    verifier: Optional[Verifier] = None
) -> Dict[str, VerificationResult]:
    """文献の全検証を実行"""
    results = {}
    
    close_verifier = False
    if verifier is None:
        verifier = Verifier()
        await verifier.__aenter__()
        close_verifier = True
    
    try:
        # DOI検証
        if work_data.get('DOI'):
            results['doi'] = await verifier.verify_doi(work_data['DOI'])
        
        # URL検証
        if work_data.get('URL'):
            results['url'] = await verifier.verify_url(work_data['URL'])
        
        # arXiv検証
        if work_data.get('arxiv_id'):
            results['arxiv'] = await verifier.verify_arxiv(work_data['arxiv_id'])
        
        # PubMed検証
        if work_data.get('pubmed_id'):
            results['pubmed'] = await verifier.verify_pubmed(work_data['pubmed_id'])
        
        # リトラクションチェック
        if work_data.get('DOI'):
            results['retraction'] = await verifier.check_retraction(work_data['DOI'])
            
            # URLが死んでいて、DOIがある場合は代替URLを探す
            if results.get('url') and results['url'].status == 'fail':
                alternatives = await verifier.find_alternative_urls(
                    work_data['DOI'],
                    work_data.get('title')
                )
                if alternatives:
                    results['url'].alternative_urls = alternatives
    
    finally:
        if close_verifier:
            await verifier.__aexit__(None, None, None)
    
    return results


if __name__ == "__main__":
    # テスト
    async def test():
        async with Verifier() as verifier:
            # DOIテスト
            result = await verifier.verify_doi("10.1037/0003-066X.39.2.124")
            print(f"DOI: {result.status} - {result.detail}")
            
            # arXivテスト
            result = await verifier.verify_arxiv("2301.00001")
            print(f"arXiv: {result.status} - {result.detail}")
    
    asyncio.run(test())
