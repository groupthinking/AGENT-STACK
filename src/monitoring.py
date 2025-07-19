"""Monitoring and observability for MCP Agent Stack."""

import time
import psutil
import asyncio
from datetime import datetime
from typing import Dict, Any
from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST
import structlog

from config import settings
from models import AgentMetrics, HealthCheck

# Configure structured logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()

# Prometheus metrics
REQUEST_COUNT = Counter('mcp_requests_total', 'Total requests processed', ['agent', 'status'])
REQUEST_DURATION = Histogram('mcp_request_duration_seconds', 'Request processing time', ['agent'])
ACTIVE_AGENTS = Gauge('mcp_active_agents', 'Number of active agents')
MEMORY_USAGE = Gauge('mcp_memory_bytes', 'Memory usage in bytes')
CPU_USAGE = Gauge('mcp_cpu_percent', 'CPU usage percentage')


class MetricsCollector:
    """Collects and manages application metrics."""
    
    def __init__(self):
        self.start_time = time.time()
        self.agent_metrics: Dict[str, AgentMetrics] = {}
        self._setup_metrics()
    
    def _setup_metrics(self):
        """Initialize agent-specific metrics."""
        agents = ['data_parser', 'summarizer', 'optimizer', 'logger']
        for agent in agents:
            self.agent_metrics[agent] = AgentMetrics(agent_name=agent)
    
    def record_request(self, agent_name: str, duration: float, success: bool = True):
        """Record a processed request."""
        status = 'success' if success else 'error'
        REQUEST_COUNT.labels(agent=agent_name, status=status).inc()
        REQUEST_DURATION.labels(agent=agent_name).observe(duration)
        
        if agent_name in self.agent_metrics:
            metrics = self.agent_metrics[agent_name]
            metrics.requests_processed += 1
            metrics.total_processing_time += duration
            metrics.average_processing_time = metrics.total_processing_time / metrics.requests_processed
            metrics.last_processed = datetime.utcnow()
            
            if not success:
                metrics.error_count += 1
    
    def update_system_metrics(self):
        """Update system-level metrics."""
        process = psutil.Process()
        memory_info = process.memory_info()
        
        MEMORY_USAGE.set(memory_info.rss)
        CPU_USAGE.set(process.cpu_percent())
        ACTIVE_AGENTS.set(len([m for m in self.agent_metrics.values() if m.requests_processed > 0]))
    
    def get_health_check(self) -> HealthCheck:
        """Generate health check response."""
        process = psutil.Process()
        memory_info = process.memory_info()
        
        return HealthCheck(
            status="healthy",
            timestamp=datetime.utcnow(),
            version=settings.app_version,
            uptime_seconds=time.time() - self.start_time,
            memory_usage_mb=memory_info.rss / 1024 / 1024,
            cpu_usage_percent=process.cpu_percent(),
            active_agents=len([m for m in self.agent_metrics.values() if m.requests_processed > 0])
        )
    
    def get_metrics_prometheus(self) -> str:
        """Get Prometheus metrics in text format."""
        self.update_system_metrics()
        return generate_latest()


class MonitoringMiddleware:
    """Middleware for request monitoring."""
    
    def __init__(self, metrics_collector: MetricsCollector):
        self.metrics = metrics_collector
    
    async def monitor_request(self, agent_name: str, func, *args, **kwargs):
        """Monitor a function call with timing and error handling."""
        start_time = time.time()
        success = True
        
        try:
            result = await func(*args, **kwargs) if asyncio.iscoroutinefunction(func) else func(*args, **kwargs)
            duration = time.time() - start_time
            self.metrics.record_request(agent_name, duration, success=True)
            logger.info("Request processed successfully", 
                       agent=agent_name, 
                       duration_ms=duration*1000,
                       success=True)
            return result
        except Exception as e:
            duration = time.time() - start_time
            success = False
            self.metrics.record_request(agent_name, duration, success=False)
            logger.error("Request processing failed",
                        agent=agent_name,
                        duration_ms=duration*1000,
                        error=str(e),
                        success=False)
            raise


# Global metrics collector
metrics_collector = MetricsCollector()
monitoring_middleware = MonitoringMiddleware(metrics_collector)