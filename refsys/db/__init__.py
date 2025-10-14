"""
データベース接続とユーティリティ
"""
import sqlite3
import os
from pathlib import Path
from typing import Optional
import asyncio
import aiosqlite

DEFAULT_DB_PATH = Path.home() / ".refsys" / "refsys.db"


def get_db_path() -> Path:
    """データベースのパスを取得"""
    db_path = os.environ.get("REFSYS_DB_PATH")
    if db_path:
        return Path(db_path)
    return DEFAULT_DB_PATH


def ensure_db_dir():
    """データベースディレクトリの作成"""
    db_path = get_db_path()
    db_path.parent.mkdir(parents=True, exist_ok=True)
    return db_path


def get_connection() -> sqlite3.Connection:
    """同期的なDB接続を取得"""
    db_path = ensure_db_dir()
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    # 外部キー制約を有効化
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


async def get_async_connection() -> aiosqlite.Connection:
    """非同期DB接続を取得"""
    db_path = ensure_db_dir()
    conn = await aiosqlite.connect(str(db_path))
    conn.row_factory = aiosqlite.Row
    await conn.execute("PRAGMA foreign_keys = ON;")
    return conn


def init_database():
    """データベースの初期化"""
    from .schema import ALL_TABLES, CREATE_INDEXES
    
    conn = get_connection()
    try:
        # テーブル作成
        for table_sql in ALL_TABLES:
            conn.execute(table_sql)
        
        # インデックス作成
        for index_sql in CREATE_INDEXES:
            conn.execute(index_sql)
        
        conn.commit()
        print(f"✅ Database initialized at: {get_db_path()}")
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        raise
    finally:
        conn.close()


async def init_database_async():
    """データベースの初期化（非同期版）"""
    from .schema import ALL_TABLES, CREATE_INDEXES
    
    conn = await get_async_connection()
    try:
        # テーブル作成
        for table_sql in ALL_TABLES:
            await conn.execute(table_sql)
        
        # インデックス作成
        for index_sql in CREATE_INDEXES:
            await conn.execute(index_sql)
        
        await conn.commit()
        print(f"✅ Database initialized at: {get_db_path()}")
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        raise
    finally:
        await conn.close()


if __name__ == "__main__":
    init_database()
