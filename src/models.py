"""Data models for MCP Agent Stack."""

from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field, validator
import uuid


class ProcessingRequest(BaseModel):
    """Input request model with validation."""
    
    content: str = Field(..., description="Content to process", min_length=1)
    request_id: Optional[str] = Field(default_factory=lambda: str(uuid.uuid4()))
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)
    priority: int = Field(default=1, ge=1, le=10, description="Processing priority")
    
    @validator('content')
    def validate_content(cls, v):
        if len(v) > 10000:  # 10KB limit
            raise ValueError("Content too large. Maximum 10,000 characters allowed.")
        return v.strip()


class ProcessingResponse(BaseModel):
    """Output response model."""
    
    request_id: str
    processed_content: str
    summary: str
    processing_time_ms: float
    agent_metadata: Dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    success: bool = True
    error_message: Optional[str] = None


class AgentMetrics(BaseModel):
    """Agent performance metrics."""
    
    agent_name: str
    requests_processed: int = 0
    total_processing_time: float = 0.0
    average_processing_time: float = 0.0
    error_count: int = 0
    last_processed: Optional[datetime] = None


class HealthCheck(BaseModel):
    """Health check response."""
    
    status: str
    timestamp: datetime
    version: str
    uptime_seconds: float
    memory_usage_mb: float
    cpu_usage_percent: float
    active_agents: int