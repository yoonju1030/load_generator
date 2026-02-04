import uuid
from datetime import datetime
from sqlalchemy import String, Float, Integer, Boolean, DateTime, Text, JSON, Uuid
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class Exec(Base):
    """요청 조건(request)과 결과(response)를 담는 실행 로그 테이블. 매 요청마다 1 row 추가."""

    __tablename__ = "exec"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    run_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)

    # ---- 요청 조건 ----
    method: Mapped[str] = mapped_column(String(10), nullable=False)
    path: Mapped[str] = mapped_column(String(2048), nullable=False)
    timeout_s: Mapped[float] = mapped_column(Float, nullable=False)
    request_headers: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    request_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    # ---- 결과 ----
    status_code: Mapped[int | None] = mapped_column(Integer, nullable=True)
    latency_ms: Mapped[float | None] = mapped_column(Float, nullable=True)
    success: Mapped[bool] = mapped_column(Boolean, nullable=False)
    error: Mapped[str | None] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
