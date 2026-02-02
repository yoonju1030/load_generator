from pydantic import BaseModel
from typing import Literal, Optional, Any

class SingleScenario(BaseModel):
    method: Literal["GET", "POST", "PUT", "DELETE", "PATCH"]
    path: str
    headers: dict[str, str]
    json: Optional[dict[str, Any]] = None
    timeout_s: float = 10.0

class RunCreateRequest(BaseModel):
    base_url: str
    duration_s: int = Field(default=60, ge=1, le=3600)
    rps: float = Field(default=10.0, gt=0)
    concurrency: int = Field(default=50, ge=1, le=5000)
    scenario: SingleScenario