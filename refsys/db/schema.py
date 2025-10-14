"""
データベーススキーマの定義
"""

CREATE_WORKS_TABLE = """
CREATE TABLE IF NOT EXISTS works (
    id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    type TEXT,
    container_title TEXT,
    issued_year INTEGER,
    doi TEXT UNIQUE,
    url TEXT,
    arxiv_id TEXT,
    pubmed_id TEXT,
    isbn TEXT,
    peer_reviewed INTEGER,
    retracted INTEGER DEFAULT 0,
    consensus_score INTEGER,
    raw_csl_json TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
);
"""

CREATE_AUTHORS_TABLE = """
CREATE TABLE IF NOT EXISTS authors (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    family TEXT,
    given TEXT,
    UNIQUE(family, given)
);
"""

CREATE_WORK_AUTHORS_TABLE = """
CREATE TABLE IF NOT EXISTS work_authors (
    work_id TEXT,
    author_id INTEGER,
    ord INTEGER,
    PRIMARY KEY (work_id, author_id),
    FOREIGN KEY (work_id) REFERENCES works(id) ON DELETE CASCADE,
    FOREIGN KEY (author_id) REFERENCES authors(id) ON DELETE CASCADE
);
"""

CREATE_CHECKS_TABLE = """
CREATE TABLE IF NOT EXISTS checks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    work_id TEXT,
    kind TEXT,
    status TEXT,
    detail TEXT,
    http_code INTEGER,
    checked_at TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (work_id) REFERENCES works(id) ON DELETE CASCADE
);
"""

CREATE_READ_EVIDENCE_TABLE = """
CREATE TABLE IF NOT EXISTS read_evidence (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    work_id TEXT,
    pdf_path TEXT,
    page INTEGER,
    dwell_secs INTEGER,
    coverage REAL,
    snippet_hash TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (work_id) REFERENCES works(id) ON DELETE CASCADE
);
"""

CREATE_CLAIM_CARDS_TABLE = """
CREATE TABLE IF NOT EXISTS claim_cards (
    id TEXT PRIMARY KEY,
    work_id TEXT,
    claim TEXT NOT NULL,
    evidence_snippet TEXT,
    page_from INTEGER,
    page_to INTEGER,
    limitations TEXT,
    verified INTEGER DEFAULT 0,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (work_id) REFERENCES works(id) ON DELETE CASCADE
);
"""

CREATE_CACHE_TABLE = """
CREATE TABLE IF NOT EXISTS cache (
    key TEXT PRIMARY KEY,
    value TEXT,
    etag TEXT,
    last_modified TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    expires_at TEXT
);
"""

ALL_TABLES = [
    CREATE_WORKS_TABLE,
    CREATE_AUTHORS_TABLE,
    CREATE_WORK_AUTHORS_TABLE,
    CREATE_CHECKS_TABLE,
    CREATE_READ_EVIDENCE_TABLE,
    CREATE_CLAIM_CARDS_TABLE,
    CREATE_CACHE_TABLE,
]

# インデックス
CREATE_INDEXES = [
    "CREATE INDEX IF NOT EXISTS idx_works_doi ON works(doi);",
    "CREATE INDEX IF NOT EXISTS idx_works_arxiv ON works(arxiv_id);",
    "CREATE INDEX IF NOT EXISTS idx_works_pubmed ON works(pubmed_id);",
    "CREATE INDEX IF NOT EXISTS idx_works_isbn ON works(isbn);",
    "CREATE INDEX IF NOT EXISTS idx_checks_work_id ON checks(work_id);",
    "CREATE INDEX IF NOT EXISTS idx_read_evidence_work_id ON read_evidence(work_id);",
    "CREATE INDEX IF NOT EXISTS idx_claim_cards_work_id ON claim_cards(work_id);",
    "CREATE INDEX IF NOT EXISTS idx_cache_expires ON cache(expires_at);",
]
