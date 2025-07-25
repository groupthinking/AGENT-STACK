"""FastAPI web server for MCP Agent Stack."""

import asyncio
from typing import Dict, Any
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse, PlainTextResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from config import settings
from models import ProcessingRequest, ProcessingResponse, HealthCheck
from agents import Orchestrator
from monitoring import metrics_collector, logger

# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Production-ready MCP Agent Stack API",
    docs_url="/docs" if settings.debug else None,
    redoc_url="/redoc" if settings.debug else None
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global orchestrator instance
orchestrator = Orchestrator()


@app.on_event("startup")
async def startup_event():
    """Initialize application on startup."""
    logger.info("Starting MCP Agent Stack API", version=settings.app_version)


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown."""
    logger.info("Shutting down MCP Agent Stack API")


@app.get("/")
async def root():
    """Root endpoint with basic info."""
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "status": "running",
        "docs": "/docs" if settings.debug else "disabled"
    }


@app.get("/health", response_model=HealthCheck)
async def health_check():
    """Health check endpoint."""
    return metrics_collector.get_health_check()


@app.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint."""
    if not settings.enable_metrics:
        raise HTTPException(status_code=404, detail="Metrics disabled")
    
    return PlainTextResponse(
        metrics_collector.get_metrics_prometheus(),
        media_type="text/plain"
    )


@app.post("/process", response_model=ProcessingResponse)
async def process_content(request: ProcessingRequest):
    """Process content through the agent pipeline."""
    try:
        logger.info("Processing request", 
                   request_id=request.request_id,
                   content_length=len(request.content))
        
        response = await orchestrator.run(
            content=request.content,
            request_id=request.request_id
        )
        
        logger.info("Request processed successfully",
                   request_id=request.request_id,
                   processing_time_ms=response.processing_time_ms)
        
        return response
        
    except Exception as e:
        logger.error("Processing failed",
                    request_id=request.request_id,
                    error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/process/simple")
async def process_simple(content: str):
    """Simple processing endpoint for backward compatibility."""
    try:
        response = await orchestrator.run(content)
        return {
            "result": response.processed_content,
            "success": response.success,
            "processing_time_ms": response.processing_time_ms
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/config")
async def get_config():
    """Get current configuration (non-sensitive)."""
    return {
        "app_name": settings.app_name,
        "app_version": settings.app_version,
        "debug": settings.debug,
        "max_summary_length": settings.max_summary_length,
        "enable_optimization": settings.enable_optimization,
        "max_input_size": settings.max_input_size,
        "enable_metrics": settings.enable_metrics
    }


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler."""
    logger.error("Unhandled exception", error=str(exc))
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )


def run_server(host: str = "0.0.0.0", port: int = 8000):
    """Run the FastAPI server."""
    uvicorn.run(
        "api:app",
        host=host,
        port=port,
        reload=settings.debug,
        log_level=settings.log_level.lower()
    )


if __name__ == "__main__":
    run_server()