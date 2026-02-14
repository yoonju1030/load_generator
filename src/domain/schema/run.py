from pydantic import BaseModel, Field, field_validator, AliasChoices
from typing import Literal, Optional, Any
import uuid

def _normalize_headers(v):
    if v is None:
        return None
    out = {}
    for k, val in (v or {}).items():
        if isinstance(val, list):
            out[k] = str(val[0]) if val else ""
        else:
            out[k] = str(val) if val is not None else ""
    return out

class SingleScenario(BaseModel):
    method: Literal["GET", "POST", "PUT", "DELETE", "PATCH"]
    path: str
    headers: Optional[dict[str, str]] = Field(None, validation_alias=AliasChoices("headers", "header"))
    json: Optional[Any] = None
    timeout_s: float = 10.0

    @field_validator("method", mode="before")
    @classmethod
    def method_upper(cls, v):
        return v.upper() if isinstance(v, str) else v

    @field_validator("headers", mode="before")
    @classmethod
    def headers_normalize(cls, v):
        return _normalize_headers(v)

class RunCreateRequest(BaseModel):
    base_url: str
    duration_s: float = Field(default=60.0, ge=0.001, le=3600)  # 0.001 이상 (Spring에서 0.5초 등 소수 가능)
    rps: float = Field(default=10.0, gt=0)
    concurrency: int = Field(default=50, ge=1, le=5000)
    run_id: str = Field(default=str(uuid.uuid4()))
    scenario: SingleScenario