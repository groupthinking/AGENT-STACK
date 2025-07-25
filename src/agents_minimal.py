"""Minimal MCP Agent orchestrator for testing without external dependencies."""

import asyncio
import time
import uuid
from typing import List, Dict, Any, Optional
from datetime import datetime


class Settings:
    """Minimal settings class."""
    app_name = "MCP Agent Stack"
    app_version = "1.0.0"
    debug = False
    max_summary_length = 100
    enable_optimization = True
    log_level = "INFO"
    max_concurrent_agents = 10
    request_timeout = 30
    enable_input_validation = True
    max_input_size = 10000
    enable_metrics = True
    metrics_port = 8000


settings = Settings()


class ProcessingRequest:
    """Minimal request model."""
    def __init__(self, content: str, request_id: Optional[str] = None):
        self.content = content
        self.request_id = request_id or str(uuid.uuid4())


class ProcessingResponse:
    """Minimal response model."""
    def __init__(self, request_id: str, processed_content: str, summary: str, 
                 processing_time_ms: float, success: bool = True, error_message: Optional[str] = None):
        self.request_id = request_id
        self.processed_content = processed_content
        self.summary = summary
        self.processing_time_ms = processing_time_ms
        self.success = success
        self.error_message = error_message


class BaseAgent:
    """Base class for all agents."""
    
    def __init__(self, name: str):
        self.name = name
    
    async def process(self, data: Any) -> Any:
        """Process data with monitoring."""
        start_time = time.time()
        try:
            result = await self._process_impl(data)
            duration = (time.time() - start_time) * 1000
            print(f"[{self.name.upper()}] Processed in {duration:.2f}ms")
            return result
        except Exception as e:
            duration = (time.time() - start_time) * 1000
            print(f"[{self.name.upper()}] Error after {duration:.2f}ms: {e}")
            raise
    
    async def _process_impl(self, data: Any) -> Any:
        """Implementation to be overridden by subclasses."""
        raise NotImplementedError


class DataParserAgent(BaseAgent):
    """Enhanced data parser with validation."""
    
    def __init__(self):
        super().__init__("data_parser")
    
    async def _process_impl(self, data: str) -> Dict[str, Any]:
        """Parse raw data into a structured dictionary."""
        if not isinstance(data, str):
            raise ValueError("Data must be a string")
        
        if len(data) > settings.max_input_size:
            raise ValueError(f"Data too large. Maximum {settings.max_input_size} characters allowed.")
        
        parsed_data = {
            "id": str(uuid.uuid4()),
            "content": data,
            "length": len(data),
            "word_count": len(data.split()),
            "timestamp": datetime.utcnow().isoformat(),
            "metadata": {
                "parser_version": "2.0.0",
                "max_length": settings.max_input_size
            }
        }
        
        return parsed_data


class SummarizerAgent(BaseAgent):
    """Enhanced summarizer with configurable length."""
    
    def __init__(self):
        super().__init__("summarizer")
    
    async def _process_impl(self, data: Dict[str, Any]) -> str:
        """Create an intelligent summary of the content."""
        content = data.get("content", "")
        
        if not content:
            return ""
        
        words = content.split()
        max_length = settings.max_summary_length
        
        if len(words) <= max_length:
            summary = content
        else:
            summary = self._create_summary(content, max_length)
        
        return summary
    
    def _create_summary(self, content: str, max_length: int) -> str:
        """Create a summary using basic NLP techniques."""
        sentences = content.split('.')
        if len(sentences) <= 1:
            return content[:max_length]
        
        summary = sentences[0].strip()
        if len(summary) > max_length:
            summary = summary[:max_length-3] + "..."
        
        return summary


class OptimizerAgent(BaseAgent):
    """Enhanced optimizer with multiple strategies."""
    
    def __init__(self):
        super().__init__("optimizer")
    
    async def _process_impl(self, content: str) -> str:
        """Optimize content using various strategies."""
        if not settings.enable_optimization:
            return content
        
        optimized = self._optimize_content(content)
        return optimized
    
    def _optimize_content(self, content: str) -> str:
        """Apply various optimization strategies."""
        optimized = ' '.join(content.split())
        
        noise_patterns = ['\n\n\n', '\t\t', '  ']
        for pattern in noise_patterns:
            optimized = optimized.replace(pattern, ' ')
        
        if optimized and not optimized.endswith(('.', '!', '?')):
            optimized += '.'
        
        return optimized.strip()


class LoggerAgent(BaseAgent):
    """Enhanced logger with structured logging."""
    
    def __init__(self):
        super().__init__("logger")
    
    async def _process_impl(self, message: str) -> None:
        """Log message with enhanced context."""
        log_data = {
            "message": message,
            "timestamp": datetime.utcnow().isoformat(),
            "log_level": "INFO"
        }
        
        print(f"[{self.name.upper()}] {message}")


class AgentFactory:
    """Factory for creating and managing agents."""
    
    @staticmethod
    def create_agents() -> List[BaseAgent]:
        """Create all agents with proper initialization."""
        return [
            DataParserAgent(),
            LoggerAgent(),  # Log parsing start
            SummarizerAgent(),
            LoggerAgent(),  # Log summarization
            OptimizerAgent(),
            LoggerAgent()   # Final logging
        ]


class LoadBalancer:
    """Enhanced load balancer with async processing."""
    
    def __init__(self, agents: List[BaseAgent]):
        self.agents = agents
    
    async def distribute(self, request: ProcessingRequest) -> ProcessingResponse:
        """Process request through the agent pipeline."""
        start_time = time.time()
        
        try:
            # Step 1: Parse data
            print(f"[LOAD_BALANCER] Starting data parsing for request {request.request_id}")
            parsed_data = await self.agents[0].process(request.content)
            
            # Step 2: Log parsing completion
            await self.agents[1].process(f"Data parsed successfully for request {request.request_id}")
            
            # Step 3: Summarize content
            print(f"[LOAD_BALANCER] Starting summarization for request {request.request_id}")
            summary = await self.agents[2].process(parsed_data)
            
            # Step 4: Log summarization completion
            await self.agents[3].process(f"Content summarized for request {request.request_id}")
            
            # Step 5: Optimize content
            print(f"[LOAD_BALANCER] Starting optimization for request {request.request_id}")
            optimized_content = await self.agents[4].process(summary)
            
            # Step 6: Final logging
            await self.agents[5].process(f"Processing completed for request {request.request_id}")
            
            processing_time = (time.time() - start_time) * 1000
            
            return ProcessingResponse(
                request_id=request.request_id,
                processed_content=optimized_content,
                summary=summary,
                processing_time_ms=processing_time
            )
            
        except Exception as e:
            processing_time = (time.time() - start_time) * 1000
            print(f"[LOAD_BALANCER] Processing failed for request {request.request_id}: {e}")
            
            return ProcessingResponse(
                request_id=request.request_id,
                processed_content="",
                summary="",
                processing_time_ms=processing_time,
                success=False,
                error_message=str(e)
            )


class Orchestrator:
    """Production-ready orchestrator with async support."""
    
    def __init__(self):
        self.agents = AgentFactory.create_agents()
        self.load_balancer = LoadBalancer(self.agents)
    
    async def run(self, content: str, request_id: Optional[str] = None) -> ProcessingResponse:
        """Process content through the agent pipeline."""
        try:
            if settings.enable_input_validation:
                if not content or not isinstance(content, str):
                    raise ValueError("Content must be a non-empty string")
            
            request = ProcessingRequest(
                content=content,
                request_id=request_id
            )
            
            print(f"[ORCHESTRATOR] Starting orchestration for request {request.request_id}")
            
            response = await self.load_balancer.distribute(request)
            
            print(f"[ORCHESTRATOR] Orchestration completed for request {request.request_id}")
            
            return response
            
        except Exception as e:
            print(f"[ORCHESTRATOR] Orchestration failed: {e}")
            raise


# For backward compatibility
def run_sync(content: str) -> str:
    """Synchronous wrapper for backward compatibility."""
    async def _run():
        orchestrator = Orchestrator()
        response = await orchestrator.run(content)
        return response.processed_content if response.success else ""
    
    return asyncio.run(_run())


if __name__ == "__main__":
    # Example usage
    async def main():
        orchestrator = Orchestrator()
        response = await orchestrator.run("This is an example input for the enhanced MCP Agent Stack with production-ready features including monitoring, logging, and error handling.")
        print(f"\nResult: {response.processed_content}")
        print(f"Processing time: {response.processing_time_ms:.2f}ms")
        print(f"Success: {response.success}")
        if response.error_message:
            print(f"Error: {response.error_message}")
    
    asyncio.run(main())