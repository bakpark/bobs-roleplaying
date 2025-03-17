from src.infra.db import DATABASE_URL
from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver

async_saver = AsyncSqliteSaver(DATABASE_URL)
