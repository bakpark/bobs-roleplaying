import aiosqlite
from datetime import datetime

DATABASE_URL = "checkpoints.db"

async def init_db():
    """
    애플리케이션 시작 시 호출하여, 테이블 구조가 없다면 생성.
    """
    async with aiosqlite.connect(DATABASE_URL) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS acting_script (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                script TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        await db.commit()
        
async def insert_acting_script(session_id, script):
    async with aiosqlite.connect(DATABASE_URL) as db:
        await db.execute("""
            INSERT INTO acting_script (session_id, script, created_at)
            VALUES (?, ?, ?)
        """, (
            session_id,
            script,
            datetime.now().isoformat()
        ))
        await db.commit()
        
async def get_acting_script(session_id):
    async with aiosqlite.connect(DATABASE_URL) as db:
        cursor = await db.execute("""
            SELECT script FROM acting_script WHERE session_id = ?
        """, (session_id,))
        result = await cursor.fetchone()
        return result[0] if result else None
