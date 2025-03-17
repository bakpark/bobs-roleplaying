import os
from datetime import datetime
from typing import Optional
import aiosqlite

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite.db")


async def init_db():
    """
    애플리케이션 시작 시 호출하여, 테이블 구조가 없다면 생성.
    """
    async with aiosqlite.connect(DATABASE_URL) as db:
        await db.execute(
            """
            CREATE TABLE IF NOT EXISTS script (
                script_id INTEGER PRIMARY KEY AUTOINCREMENT,
                script_json TEXT NOT NULL,
                translated_json TEXT DEFAULT NULL,
                translated_language TEXT DEFAULT NULL,
                description TEXT DEFAULT NULL,
                tags TEXT DEFAULT NULL,
                created_by TEXT NOT NULL,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """
        )
        await db.commit()


async def insert_script(script, created_by) -> Optional[int]:
    async with aiosqlite.connect(DATABASE_URL) as db:
        cursor = await db.execute(
            """
            INSERT INTO script (script_json, created_by, updated_at)
            VALUES (?, ?, ?)
        """,
            (script, created_by, datetime.now().isoformat()),
        )
        await db.commit()
        return cursor.lastrowid


async def update_script_info(script_id, translated_json, language, description, tags):
    async with aiosqlite.connect(DATABASE_URL) as db:
        await db.execute(
            """ 
            UPDATE script
            SET translated_json = ?, translated_language = ?, description = ?, tags = ?, updated_at = ?
            WHERE script_id = ?
        """,
            (
                translated_json,
                language,
                description,
                tags,
                datetime.now().isoformat(),
                script_id,
            ),
        )
        await db.commit()


async def get_script(script_id):
    async with aiosqlite.connect(DATABASE_URL) as db:
        cursor = await db.execute(
            """
            SELECT script_json, translated_json, translated_language, description, tags FROM script WHERE script_id = ?
        """,
            (script_id,),
        )
        result = await cursor.fetchone()
        return result[0] if result else None


async def get_script_list(email: str):
    async with aiosqlite.connect(DATABASE_URL) as db:
        cursor = await db.execute(
            """
            SELECT * FROM script WHERE created_by = ?
        """,
            (email),
        )
        result = await cursor.fetchall()
        return result
