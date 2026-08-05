# MCP Agent Stack Onboarding Guide


## Overview


The **MCP Agent Stack** is a production-ready, modular system for orchestrating specialized agents to process textual content through a defined pipeline. The system serves developers and applications that need to transform text content through a series of operations like parsing, summarization, and optimization.


### Purpose and Users
- **What it does**: Processes text content through a sequential pipeline of specialized agents (parsing → summarization → optimization → logging)
- **Who uses it**: Developers building applications that need structured text processing, content analysis systems, and AI/ML workflows requiring text preprocessing
- **Key capabilities**: 
  - Asynchronous request processing with FastAPI
  - Comprehensive monitoring with Prometheus/Grafana
  - Production-ready features (Docker, Kubernetes, CI/CD, SBOM)
  - Modular architecture allowing easy agent customization


### Architecture
The system follows a pipeline pattern where an `Orchestrator` coordinates a `LoadBalancer` that sequentially executes specialized agents. Each request flows through: DataParser → Summarizer → Optimizer → Logger, with comprehensive monitoring at each step.


## Project Organization


### Core Systems and Services


1. **FastAPI Application** (`src/api.py`) - Main web interface exposing REST endpoints
2. **Agent Pipeline System** (`src/agents.py`) - Core orchestration logic with specialized processing agents
3. **Configuration Management** (`src/config.py`) - Centralized settings using Pydantic
4. **Monitoring and Observability** (`src/monitoring.py`) - Prometheus metrics and health checks
5. **Data Models** (`src/models.py`) - Request/response schemas and data validation


### Directory Structure


```
├── src/                          # Core application code
│   ├── api.py                   # FastAPI application and endpoints
│   ├── agents.py                # Main agent orchestration system
│   ├── agents_minimal.py        # Lightweight agent implementation
│   ├── config.py                # Configuration management
│   ├── models.py                # Data models and schemas
│   ├── monitoring.py            # Metrics collection and health checks
│   └── __init__.py              # Package initialization
├── .github/workflows/           # CI/CD automation
│   ├── test.yml                # Automated testing on PRs
│   ├── release.yml             # Semantic release automation
│   ├── docs.yml                # Documentation deployment
│   └── sbom.yml                # Software Bill of Materials generation
├── docs/                        # Documentation source
├── monitoring/                  # Monitoring configuration
│   ├── prometheus.yml          # Prometheus scraping config
│   └── grafana/                # Grafana dashboards and datasources
├── docker-compose.yml           # Multi-container orchestration
├── Dockerfile                   # Container build definition
├── requirements.txt             # Python dependencies
└── mkdocs.yml                  # Documentation site configuration
```


### Main Components


**Primary Classes:**
- `Orchestrator` - Central coordinator managing the entire processing workflow
- `LoadBalancer` - Manages sequential execution of agents in the pipeline
- `BaseAgent` - Abstract base class for all processing agents
- `MetricsCollector` - Aggregates performance metrics and system health data
- `MonitoringMiddleware` - Wraps agent calls for timing and error tracking


**Key Endpoints:**
- `POST /process` - Main content processing endpoint
- `GET /health` - System health check
- `GET /metrics` - Prometheus metrics export
- `GET /config` - Configuration inspection


## Glossary of Codebase-Specific Terms


### Core System Components


**MCP Agent Stack** - The overall modular agent orchestration system for text processing  
*Location: Throughout codebase, primary definition in README.md*


**Orchestrator** - `class Orchestrator:` Central coordinator that initializes agents and manages processing requests  
*Location: src/agents.py:193, primary method: `async def run(content: str)`*


**LoadBalancer** - `class LoadBalancer:` Manages sequential execution of agents (not network load balancing)  
*Location: src/agents.py:146, key method: `async def distribute(request: ProcessingRequest)`*


### Agent System


**BaseAgent** - `class BaseAgent(ABC):` Abstract base class defining the standard agent interface  
*Location: src/agents.py:14, key methods: `process()`, `_process_impl()`*


**DataParserAgent** - `class DataParserAgent(BaseAgent):` First agent that validates and structures input text  
*Location: src/agents.py:31, processes raw strings into structured dictionaries*


**SummarizerAgent** - `class SummarizerAgent(BaseAgent):` Generates content summaries with configurable length  
*Location: src/agents.py:58, respects `settings.max_summary_length`*


**OptimizerAgent** - `class OptimizerAgent(BaseAgent):` Refines content by removing noise and formatting  
*Location: src/agents.py:89, controlled by `settings.enable_optimization`*


**LoggerAgent** - `class LoggerAgent(BaseAgent):` Structured logging throughout the processing pipeline  
*Location: src/agents.py:117, outputs JSON-formatted logs*


**AgentFactory** - `class AgentFactory:` Static factory creating the predefined sequence of agents  
*Location: src/agents.py:135, method: `create_agents() -> List[BaseAgent]`*


### Data Models


**ProcessingRequest** - `class ProcessingRequest(BaseModel):` Input data model for content processing  
*Location: src/models.py:14, fields: content, request_id, metadata, priority*


**ProcessingResponse** - `class ProcessingResponse(BaseModel):` Output data model with results and metadata  
*Location: src/models.py:27, includes processed_content, summary, timing, success status*


**AgentMetrics** - `class AgentMetrics(BaseModel):` Performance statistics for individual agents  
*Location: src/models.py:39, tracks requests_processed, processing_time, error_count*


**HealthCheck** - `class HealthCheck(BaseModel):` System health status including resource usage  
*Location: src/models.py:48, includes status, uptime, memory, CPU, active agents*


### Monitoring System


**MetricsCollector** - `class MetricsCollector:` Aggregates and exposes Prometheus metrics  
*Location: src/monitoring.py:46, methods: `record_request()`, `get_health_check()`*


**MonitoringMiddleware** - `class MonitoringMiddleware:` Wraps agent calls for performance monitoring  
*Location: src/monitoring.py:101, key method: `monitor_request(agent_name, func, *args)`*


**Settings** - `class Settings(BaseSettings):` Centralized configuration using Pydantic settings  
*Location: src/config.py:9, includes app settings, agent behavior, performance limits*


### Key Methods and Functions


**run_sync** - `def run_sync(content: str) -> str:` Synchronous wrapper for backward compatibility  
*Location: src/agents.py:233, internally uses asyncio.run()*


**distribute** - Core LoadBalancer method managing agent pipeline execution  
*Location: src/agents.py:150, orchestrates sequential agent processing*


**process** - `async def process(data: Any) -> Any:` Standard agent interface with monitoring  
*Location: src/agents.py:20, wraps `_process_impl()` with middleware*


**_process_impl** - `async def _process_impl(data: Any) -> Any:` Abstract method for agent logic  
*Location: src/agents.py:26, must be implemented by concrete agent classes*


**monitor_request** - Middleware method for timing and error tracking around function calls  
*Location: src/monitoring.py:106, records metrics and handles exceptions*


**record_request** - `def record_request(agent_name: str, duration: float, success: bool):` Metrics recording  
*Location: src/monitoring.py:56, updates Prometheus counters and timers*


**get_metrics_prometheus** - `def get_metrics_prometheus() -> str:` Exports metrics in Prometheus format  
*Location: src/monitoring.py:96, returns text format for scraping*


**update_system_metrics** - Updates system-level metrics (CPU, memory, active agents)  
*Location: src/monitoring.py:73, uses psutil for resource monitoring*
