# MCP Agent Stack

## Overview

**Production-ready** modular MCP agent orchestration system with comprehensive monitoring, security, and scalability features. The orchestrator coordinates DataParser, Summarizer, Optimizer and Logger agents to process input text through a robust pipeline.

Documentation is available in the [docs](docs/index.md) folder and on the project site.

## 🚀 Production Features

- ✅ **Async Processing** - High-performance concurrent request handling
- ✅ **Comprehensive Monitoring** - Prometheus metrics, structured logging, health checks
- ✅ **Security Hardened** - Input validation, non-root containers, secure defaults
- ✅ **Containerized** - Docker & Docker Compose ready
- ✅ **API-First** - FastAPI REST API with OpenAPI documentation
- ✅ **Configuration Management** - Environment-based settings with validation
- ✅ **Error Handling** - Robust error handling and recovery
- ✅ **Testing Suite** - Comprehensive unit and integration tests

## Quick Start

### Docker Deployment (Recommended)

```bash
# Clone repository
git clone <repository-url>
cd mcp-agent-stack

# Start with Docker Compose
docker-compose up -d

# Test the API
curl http://localhost:8000/health
curl -X POST http://localhost:8000/process \
  -H "Content-Type: application/json" \
  -d '{"content": "Test content for processing"}'
```

### Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run tests
pytest src/

# Start development server
python -m uvicorn src.api:app --reload --host 0.0.0.0 --port 8000
```

## API Endpoints

- `GET /` - Application info
- `GET /health` - Health check with system metrics
- `GET /metrics` - Prometheus metrics
- `POST /process` - Process content through agent pipeline
- `POST /process/simple` - Simple processing endpoint
- `GET /config` - Current configuration (non-sensitive)

## Architecture

### Core Components

1. **Orchestrator** - Coordinates the agent pipeline
2. **LoadBalancer** - Manages request distribution
3. **Agents** - Specialized processing units:
   - **DataParserAgent** - Input validation and structuring
   - **SummarizerAgent** - Content summarization
   - **OptimizerAgent** - Content optimization
   - **LoggerAgent** - Structured logging

### Monitoring Stack

- **Prometheus** - Metrics collection
- **Grafana** - Metrics visualization
- **Structured Logging** - JSON-formatted logs
- **Health Checks** - Application health monitoring

## Configuration

Environment variables control all aspects of the application:

```bash
# Core settings
APP_NAME=MCP Agent Stack
APP_VERSION=1.0.0
DEBUG=false

# Agent settings
MAX_SUMMARY_LENGTH=100
ENABLE_OPTIMIZATION=true
MAX_INPUT_SIZE=10000

# Monitoring
ENABLE_METRICS=true
LOG_LEVEL=INFO
```

## Deployment

### Production Deployment

See [DEPLOYMENT.md](DEPLOYMENT.md) for comprehensive production deployment guide including:

- Security hardening
- Monitoring setup
- Scaling strategies
- Backup procedures
- Troubleshooting guide

### Kubernetes Deployment

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: mcp-agent-stack
spec:
  replicas: 3
  selector:
    matchLabels:
      app: mcp-agent-stack
  template:
    metadata:
      labels:
        app: mcp-agent-stack
    spec:
      containers:
      - name: mcp-agent-stack
        image: mcp-agent-stack:latest
        ports:
        - containerPort: 8000
        env:
        - name: DEBUG
          value: "false"
```

## Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src

# Run specific test suite
pytest src/test_production.py
```

## Monitoring & Observability

### Metrics Available

- Request rate and latency
- Error rates by agent
- Memory and CPU usage
- Processing pipeline metrics

### Logging

Structured JSON logging with correlation IDs for request tracing.

### Health Checks

Comprehensive health checks including:
- Application status
- System resource usage
- Agent availability

## Security Features

- Input validation and sanitization
- Non-root container execution
- Environment-based configuration
- Secure defaults
- Comprehensive error handling

## Performance

- Async request processing
- Configurable concurrency limits
- Resource usage monitoring
- Horizontal scaling support

## Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

## License

[Add your license here]

## Support

For production support and issues:
1. Check the [DEPLOYMENT.md](DEPLOYMENT.md) troubleshooting section
2. Review application logs and metrics
3. Contact the development team

---

**Status: Production Ready** ✅

This system is ready for production deployment with comprehensive monitoring, security, and scalability features.

