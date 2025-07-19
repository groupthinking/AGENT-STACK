# MCP Agent Stack - Production Deployment Guide

## Overview

This guide covers deploying the MCP Agent Stack to production environments with monitoring, security, and scalability considerations.

## Prerequisites

- Docker and Docker Compose installed
- Python 3.11+ (for local development)
- Git
- At least 2GB RAM and 1 CPU core available

## Quick Start

### 1. Clone and Setup

```bash
git clone <repository-url>
cd mcp-agent-stack
```

### 2. Environment Configuration

Create a `.env` file in the root directory:

```bash
# Application settings
APP_NAME=MCP Agent Stack
APP_VERSION=1.0.0
DEBUG=false

# Agent settings
MAX_SUMMARY_LENGTH=100
ENABLE_OPTIMIZATION=true
LOG_LEVEL=INFO

# Performance settings
MAX_CONCURRENT_AGENTS=10
REQUEST_TIMEOUT=30

# Security settings
ENABLE_INPUT_VALIDATION=true
MAX_INPUT_SIZE=10000

# Monitoring settings
ENABLE_METRICS=true
METRICS_PORT=8000

# External services (optional)
OPENAI_API_KEY=your_openai_key_here
ANTHROPIC_API_KEY=your_anthropic_key_here
```

### 3. Docker Deployment

#### Option A: Docker Compose (Recommended)

```bash
# Build and start all services
docker-compose up -d

# View logs
docker-compose logs -f mcp-agent-stack

# Stop services
docker-compose down
```

#### Option B: Docker Only

```bash
# Build the image
docker build -t mcp-agent-stack .

# Run the container
docker run -d \
  --name mcp-agent-stack \
  -p 8000:8000 \
  --env-file .env \
  mcp-agent-stack
```

### 4. Verify Deployment

```bash
# Health check
curl http://localhost:8000/health

# Test processing
curl -X POST http://localhost:8000/process \
  -H "Content-Type: application/json" \
  -d '{"content": "Test content for processing"}'

# View metrics
curl http://localhost:8000/metrics
```

## Production Deployment

### 1. Security Considerations

#### Environment Variables
- Never commit API keys to version control
- Use secrets management (AWS Secrets Manager, HashiCorp Vault, etc.)
- Rotate keys regularly

#### Network Security
```bash
# Configure firewall rules
sudo ufw allow 8000/tcp  # Application port
sudo ufw allow 9090/tcp  # Prometheus (if exposed)
sudo ufw allow 3000/tcp  # Grafana (if exposed)
```

#### Container Security
```bash
# Run with security options
docker run --security-opt no-new-privileges \
  --cap-drop=ALL \
  --read-only \
  -v /app/logs:/app/logs:rw \
  mcp-agent-stack
```

### 2. Monitoring Setup

#### Prometheus Configuration
The `monitoring/prometheus.yml` file is already configured. Access Prometheus at:
- URL: http://localhost:9090
- Default targets: mcp-agent-stack:8000

#### Grafana Setup
1. Access Grafana: http://localhost:3000
2. Login: admin/admin
3. Add Prometheus as data source: http://prometheus:9090
4. Import dashboards for monitoring

#### Key Metrics to Monitor
- Request rate and latency
- Error rates
- Memory and CPU usage
- Agent processing times

### 3. Scaling Considerations

#### Horizontal Scaling
```bash
# Scale the service
docker-compose up -d --scale mcp-agent-stack=3

# Use a load balancer (nginx example)
docker run -d \
  --name nginx-lb \
  -p 80:80 \
  -v $(pwd)/nginx.conf:/etc/nginx/nginx.conf \
  nginx
```

#### Resource Limits
```yaml
# In docker-compose.yml
services:
  mcp-agent-stack:
    deploy:
      resources:
        limits:
          cpus: '1.0'
          memory: 1G
        reservations:
          cpus: '0.5'
          memory: 512M
```

### 4. Backup and Recovery

#### Data Backup
```bash
# Backup logs
tar -czf logs-backup-$(date +%Y%m%d).tar.gz logs/

# Backup configuration
cp .env .env.backup
cp docker-compose.yml docker-compose.yml.backup
```

#### Recovery Procedures
```bash
# Restore from backup
tar -xzf logs-backup-YYYYMMDD.tar.gz
cp .env.backup .env
docker-compose up -d
```

## Development Deployment

### 1. Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run tests
pytest src/

# Start development server
python -m uvicorn src.api:app --reload --host 0.0.0.0 --port 8000
```

### 2. Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src

# Run specific test file
pytest src/test_production.py
```

## Troubleshooting

### Common Issues

#### 1. Container Won't Start
```bash
# Check logs
docker-compose logs mcp-agent-stack

# Check resource usage
docker stats mcp-agent-stack

# Verify environment variables
docker-compose exec mcp-agent-stack env
```

#### 2. High Memory Usage
- Check for memory leaks in application
- Increase container memory limits
- Monitor with: `docker stats`

#### 3. Slow Response Times
- Check CPU usage: `docker stats`
- Review agent processing times in metrics
- Consider scaling horizontally

#### 4. Health Check Failures
```bash
# Manual health check
curl -v http://localhost:8000/health

# Check container status
docker-compose ps

# Restart service
docker-compose restart mcp-agent-stack
```

### Debug Mode

Enable debug mode for detailed logging:

```bash
# Set environment variable
export DEBUG=true

# Or in docker-compose.yml
environment:
  - DEBUG=true
```

## Performance Optimization

### 1. Configuration Tuning

```bash
# Optimize for high throughput
MAX_CONCURRENT_AGENTS=50
REQUEST_TIMEOUT=60
MAX_INPUT_SIZE=50000

# Optimize for low latency
MAX_CONCURRENT_AGENTS=5
REQUEST_TIMEOUT=10
```

### 2. Resource Allocation

```yaml
# High-performance configuration
services:
  mcp-agent-stack:
    deploy:
      resources:
        limits:
          cpus: '4.0'
          memory: 4G
        reservations:
          cpus: '2.0'
          memory: 2G
```

## Security Checklist

- [ ] Environment variables secured
- [ ] Non-root user in container
- [ ] Network access restricted
- [ ] Secrets management implemented
- [ ] Regular security updates
- [ ] Monitoring and alerting configured
- [ ] Backup procedures tested
- [ ] Disaster recovery plan documented

## Support

For issues and questions:
1. Check the troubleshooting section
2. Review application logs
3. Check monitoring dashboards
4. Contact the development team

## Version History

- v1.0.0: Initial production release
- Enhanced monitoring and observability
- Docker containerization
- Comprehensive testing suite