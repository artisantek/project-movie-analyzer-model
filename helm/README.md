# Movie Analyzer Helm Chart

A Helm chart for deploying the Movie Analyzer application with sentiment analysis capabilities using **AWS RDS PostgreSQL**.

## Overview

This Helm chart deploys a complete movie review analysis system configured to use external AWS RDS PostgreSQL database.

## Prerequisites

- Kubernetes cluster (1.19+)
- Helm 3.0+
- kubectl configured to access your cluster
- **AWS RDS PostgreSQL database** - See `../../RDS_SETUP.md` for setup instructions

## Installation

### 1. Configure RDS Connection

Update `values.yaml` with your RDS endpoint:
```yaml
backend:
  env:
    DB_HOST: "your-actual-rds-endpoint.region.rds.amazonaws.com"
```

### 2. Deploy with Helm

```bash
# Install with default values (after updating RDS endpoint)
helm install movie-analyzer ./deploy/helm --namespace movie-analyzer --create-namespace

# Install with custom values
helm install movie-analyzer ./deploy/helm \
  --namespace movie-analyzer --create-namespace \
  --set backend.env.DB_HOST="your-rds-endpoint.region.rds.amazonaws.com"

# Upgrade
helm upgrade movie-analyzer ./deploy/helm --namespace movie-analyzer

# Uninstall (RDS database remains unaffected)
helm uninstall movie-analyzer --namespace movie-analyzer
```

## Configuration

Service configurations:
- **Backend**: 1 replica, 512Mi/500m requests, 1Gi/1000m limits (connects to RDS)
- **Frontend**: 1 replica, NodePort 30000
- **Model**: 1 replica, 256Mi/250m requests, 512Mi/500m limits  
- **Database**: External AWS RDS PostgreSQL (not containerized)

## Accessing the Application

Frontend available at: http://localhost:30000

## Values

See `values.yaml` for all configurable parameters. Key RDS-related configurations:

```yaml
backend:
  env:
    DB_HOST: "your-rds-endpoint.region.rds.amazonaws.com"  # Update this
    DB_PORT: "5432"
    DB_NAME: "moviereviews"
  secret:
    DB_USERNAME: bW92aWV1c2Vy  # movieuser (base64)
    DB_PASSWORD: bW92aWVwYXNz  # moviepass (base64)
```

## Troubleshooting

**Backend Connection Issues:**
```bash
# Check pod logs
kubectl logs -l app=backend -n movie-analyzer

# Check pod status
kubectl get pods -n movie-analyzer
```

**Common Issues:**
- Backend pods CrashLoopBackOff → Verify RDS endpoint and credentials
- Database connection timeouts → Check RDS security groups
- Schema errors → Ensure RDS database is initialized with `database/init.sql` 