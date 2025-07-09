# MCP Agent Stack

## Overview
Modular, versioned MCP agent orchestration system with CI/CD, SBOM, and staging deployment readiness. The orchestrator coordinates the DataParser, Summarizer, Optimizer and Logger agents to process input text.

## Setup
```bash
pip install -r requirements.txt
```

### Running the orchestrator
```bash
python src/agents.py
```

### Running tests
```bash
python -m unittest discover src
```

## Deployment
- GitHub Actions auto-bumps version
- SBOM generated on release
- Canary deploy stub included
