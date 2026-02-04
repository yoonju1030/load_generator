import os
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from src.db.models import Base

# MariaDB async: mariadb+asyncmy://user:password@host:port/database
# 기본값은 로컬 개발용; 운영에서는 환경변수 DATABASE_URL 로 덮어쓰기
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "mariadb+asyncmy://root:password@127.0.0.1:3306/loadgen",
)

engine = create_async_engine(
    DATABASE_URL,
    echo=os.getenv("SQL_ECHO", "0").lower() in ("1", "true"),
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
)

async_session_factory = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
)


async def get_session() -> AsyncSession:
    async with async_session_factory() as session:
        yield session


async def init_db() -> None:
    """앱 시작 시 테이블 생성."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
