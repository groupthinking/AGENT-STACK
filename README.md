# MCP Agent Stack

## Overview
Modular, versioned MCP agent orchestration system with CI/CD, SBOM, and staging deployment readiness.

## Setup
pip install -r requirements.txt
python src/agents.py

## Deployment
- GitHub Actions auto-bumps version
- SBOM generated on release
- Canary deploy stub included
