"""Production tests for MCP Agent Stack."""

import pytest
import asyncio
from unittest.mock import patch, MagicMock
import json

from config import settings
from models import ProcessingRequest, ProcessingResponse
from agents import Orchestrator, DataParserAgent, SummarizerAgent, OptimizerAgent
from monitoring import MetricsCollector, MonitoringMiddleware


class TestProductionAgents:
    """Test production-ready agent functionality."""
    
    @pytest.mark.asyncio
    async def test_data_parser_agent(self):
        """Test enhanced data parser agent."""
        agent = DataParserAgent()
        result = await agent.process("Test content")
        
        assert isinstance(result, dict)
        assert "id" in result
        assert result["content"] == "Test content"
        assert result["length"] == 12
        assert result["word_count"] == 2
    
    @pytest.mark.asyncio
    async def test_data_parser_validation(self):
        """Test data parser input validation."""
        agent = DataParserAgent()
        
        # Test invalid input type
        with pytest.raises(ValueError, match="Data must be a string"):
            await agent.process(123)
        
        # Test oversized input
        large_content = "x" * (settings.max_input_size + 1)
        with pytest.raises(ValueError, match="Data too large"):
            await agent.process(large_content)
    
    @pytest.mark.asyncio
    async def test_summarizer_agent(self):
        """Test enhanced summarizer agent."""
        agent = SummarizerAgent()
        data = {"content": "This is a test sentence. This is another sentence."}
        
        result = await agent.process(data)
        
        assert isinstance(result, str)
        assert len(result) <= settings.max_summary_length
        assert "This is a test sentence" in result
    
    @pytest.mark.asyncio
    async def test_optimizer_agent(self):
        """Test enhanced optimizer agent."""
        agent = OptimizerAgent()
        content = "  This   has   extra   spaces  \n\n\n"
        
        result = await agent.process(content)
        
        assert isinstance(result, str)
        assert "  " not in result  # No double spaces
        assert result.endswith('.')  # Proper sentence ending
    
    @pytest.mark.asyncio
    async def test_optimizer_disabled(self):
        """Test optimizer when disabled."""
        original_setting = settings.enable_optimization
        settings.enable_optimization = False
        
        try:
            agent = OptimizerAgent()
            content = "  Test  content  "
            result = await agent.process(content)
            assert result == content  # Should return unchanged
        finally:
            settings.enable_optimization = original_setting


class TestOrchestrator:
    """Test production orchestrator."""
    
    @pytest.mark.asyncio
    async def test_orchestrator_success(self):
        """Test successful orchestration."""
        orchestrator = Orchestrator()
        content = "This is a test input for the enhanced MCP Agent Stack."
        
        response = await orchestrator.run(content)
        
        assert isinstance(response, ProcessingResponse)
        assert response.success is True
        assert response.request_id is not None
        assert response.processing_time_ms > 0
        assert response.processed_content is not None
        assert response.summary is not None
    
    @pytest.mark.asyncio
    async def test_orchestrator_validation(self):
        """Test input validation in orchestrator."""
        orchestrator = Orchestrator()
        
        # Test empty content
        with pytest.raises(ValueError, match="Content must be a non-empty string"):
            await orchestrator.run("")
        
        # Test non-string content
        with pytest.raises(ValueError, match="Content must be a non-empty string"):
            await orchestrator.run(None)
    
    @pytest.mark.asyncio
    async def test_orchestrator_error_handling(self):
        """Test error handling in orchestrator."""
        orchestrator = Orchestrator()
        
        # Test with oversized content
        large_content = "x" * (settings.max_input_size + 1)
        response = await orchestrator.run(large_content)
        
        assert response.success is False
        assert response.error_message is not None
        assert "Data too large" in response.error_message


class TestMonitoring:
    """Test monitoring and metrics functionality."""
    
    def test_metrics_collector(self):
        """Test metrics collector functionality."""
        collector = MetricsCollector()
        
        # Test recording requests
        collector.record_request("test_agent", 1.5, success=True)
        collector.record_request("test_agent", 0.5, success=False)
        
        # Test health check
        health = collector.get_health_check()
        assert health.status == "healthy"
        assert health.version == settings.app_version
        assert health.uptime_seconds > 0
    
    @pytest.mark.asyncio
    async def test_monitoring_middleware(self):
        """Test monitoring middleware."""
        collector = MetricsCollector()
        middleware = MonitoringMiddleware(collector)
        
        # Test successful function call
        async def test_func(x):
            return x * 2
        
        result = await middleware.monitor_request("test_agent", test_func, 5)
        assert result == 10
    
    @pytest.mark.asyncio
    async def test_monitoring_middleware_error(self):
        """Test monitoring middleware with errors."""
        collector = MetricsCollector()
        middleware = MonitoringMiddleware(collector)
        
        # Test function that raises exception
        async def error_func():
            raise ValueError("Test error")
        
        with pytest.raises(ValueError, match="Test error"):
            await middleware.monitor_request("test_agent", error_func)


class TestModels:
    """Test data models."""
    
    def test_processing_request_validation(self):
        """Test ProcessingRequest validation."""
        # Valid request
        request = ProcessingRequest(content="Test content")
        assert request.content == "Test content"
        assert request.request_id is not None
        
        # Test oversized content
        large_content = "x" * 10001
        with pytest.raises(ValueError, match="Content too large"):
            ProcessingRequest(content=large_content)
    
    def test_processing_response(self):
        """Test ProcessingResponse model."""
        response = ProcessingResponse(
            request_id="test-123",
            processed_content="result",
            summary="summary",
            processing_time_ms=100.5
        )
        
        assert response.request_id == "test-123"
        assert response.processed_content == "result"
        assert response.processing_time_ms == 100.5
        assert response.success is True


class TestConfiguration:
    """Test configuration management."""
    
    def test_settings_defaults(self):
        """Test default settings."""
        assert settings.app_name == "MCP Agent Stack"
        assert settings.app_version == "1.0.0"
        assert settings.max_summary_length == 100
        assert settings.enable_optimization is True
    
    def test_settings_environment_override(self):
        """Test environment variable override."""
        # This would be tested with actual env vars in integration tests
        assert hasattr(settings, 'max_input_size')
        assert hasattr(settings, 'enable_metrics')


# Integration tests
class TestIntegration:
    """Integration tests for the complete system."""
    
    @pytest.mark.asyncio
    async def test_full_pipeline(self):
        """Test the complete processing pipeline."""
        orchestrator = Orchestrator()
        content = "This is a comprehensive test of the MCP Agent Stack with multiple sentences. It should process through all agents and return a properly formatted result."
        
        response = await orchestrator.run(content)
        
        # Verify response structure
        assert response.success is True
        assert len(response.processed_content) > 0
        assert len(response.summary) > 0
        assert response.processing_time_ms > 0
        
        # Verify processing quality
        assert response.processed_content.endswith('.')
        assert len(response.summary) <= settings.max_summary_length
    
    @pytest.mark.asyncio
    async def test_concurrent_processing(self):
        """Test concurrent request processing."""
        orchestrator = Orchestrator()
        contents = [
            f"Test content {i} for concurrent processing."
            for i in range(5)
        ]
        
        # Process multiple requests concurrently
        tasks = [orchestrator.run(content) for content in contents]
        responses = await asyncio.gather(*tasks)
        
        assert len(responses) == 5
        for response in responses:
            assert response.success is True
            assert response.processing_time_ms > 0


if __name__ == "__main__":
    pytest.main([__file__])