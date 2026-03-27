from pydantic import BaseModel, Field
from typing import Optional, List

class AgentSecConfig(BaseModel):
    tenant_id: str
    app_id: str
    collector_url: str
    sampling_rate: float = 1.0
    pii_redaction_enabled: bool = True
