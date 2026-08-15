# 🚀 Deployment Guide

## Miracle Birds - Enterprise Deployment Architecture

**Version:** 1.0  
**Last Updated:** July 13, 2026  
**Target Environment:** AWS + Kubernetes

---

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Prerequisites](#prerequisites)
3. [AWS Infrastructure (Terraform)](#aws-infrastructure-terraform)
4. [Kubernetes Deployment](#kubernetes-deployment)
5. [CI/CD Pipeline](#cicd-pipeline)
6. [Monitoring Stack](#monitoring-stack)
7. [Scaling Strategy](#scaling-strategy)
8. [Disaster Recovery](#disaster-recovery)

---

## Architecture Overview

```
┌──────────────────────────────────────────────────────────────┐
│                    AWS Production Architecture                │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  Internet ──► CloudFront CDN ──► ALB (Load Balancer)        │
│                                         │                    │
│              ┌──────────────────────────┤                    │
│              │                          │                    │
│         EKS Cluster                     │                    │
│         ├── Frontend (2-8 pods)         │                    │
│         ├── Backend API (3-10 pods)     │                    │
│         ├── AI Engine (2-6 pods)        │                    │
│         ├── ML Engine (2-5 pods)        │                    │
│         ├── CRM Integration (2-4 pods)  │                    │
│         └── Security Engine (2-4 pods) │                    │
│                                         │                    │
│  Data Layer:                            │                    │
│  ├── RDS PostgreSQL (Multi-AZ)         │                    │
│  ├── ElastiCache Redis (Cluster)        │                    │
│  └── S3 (Assets + Backups)             │                    │
│                                         │                    │
│  Supporting Services:                   │                    │
│  ├── Secrets Manager                    │                    │
│  ├── CloudWatch Logs                    │                    │
│  ├── Route 53 (DNS)                     │                    │
│  └── ACM (SSL Certificates)            │                    │
└──────────────────────────────────────────────────────────────┘
```

---

## Prerequisites

### Tools Required

```bash
# Install required CLI tools

# AWS CLI v2
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip && sudo ./aws/install

# Terraform >= 1.6
wget https://releases.hashicorp.com/terraform/1.6.0/terraform_1.6.0_linux_amd64.zip
unzip terraform_1.6.0_linux_amd64.zip && sudo mv terraform /usr/local/bin/

# kubectl
curl -LO https://dl.k8s.io/release/v1.29.0/bin/linux/amd64/kubectl
sudo install -o root -g root -m 0755 kubectl /usr/local/bin/kubectl

# Helm >= 3.13
curl https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash

# Docker >= 24
curl -fsSL https://get.docker.com | sh
```

### AWS Permissions

The deploying IAM user/role needs:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "eks:*",
        "ec2:*",
        "rds:*",
        "elasticache:*",
        "s3:*",
        "iam:*",
        "secretsmanager:*",
        "cloudwatch:*",
        "route53:*",
        "acm:*"
      ],
      "Resource": "*"
    }
  ]
}
```

---

## AWS Infrastructure (Terraform)

### Initial Setup

```bash
# 1. Configure AWS credentials
aws configure
# AWS Access Key ID: your_access_key
# AWS Secret Access Key: your_secret_key
# Default region: us-east-1

# 2. Create S3 bucket for Terraform state (one-time)
aws s3 mb s3://miracle-birds-terraform-state --region us-east-1
aws s3api put-bucket-versioning \
  --bucket miracle-birds-terraform-state \
  --versioning-configuration Status=Enabled

# 3. Create DynamoDB table for state locking (one-time)
aws dynamodb create-table \
  --table-name miracle-birds-terraform-locks \
  --attribute-definitions AttributeName=LockID,AttributeType=S \
  --key-schema AttributeName=LockID,KeyType=HASH \
  --billing-mode PAY_PER_REQUEST \
  --region us-east-1

# 4. Navigate to terraform directory
cd infrastructure/terraform

# 5. Initialize Terraform
terraform init

# 6. Create terraform.tfvars (DO NOT commit to git)
cat > terraform.tfvars <<EOF
aws_region      = "us-east-1"
environment     = "production"
redis_auth_token = "your-secure-redis-token"
EOF

# 7. Plan deployment
terraform plan -out=tfplan

# 8. Apply (creates all AWS resources)
terraform apply tfplan
```

### Resource Creation Time

```
VPC + Subnets:           2-3 minutes
EKS Cluster:            15-20 minutes
RDS PostgreSQL:         10-15 minutes
ElastiCache Redis:       5-10 minutes
S3 Buckets:              < 1 minute
Secrets Manager:         < 1 minute
Total:                  ~35-50 minutes
```

---

## Kubernetes Deployment

### Connect to EKS

```bash
# Get kubeconfig
aws eks update-kubeconfig \
  --name miracle-birds-production \
  --region us-east-1

# Verify connection
kubectl cluster-info
kubectl get nodes
```

### Create Namespace and Secrets

```bash
# Create namespace
kubectl create namespace miracle-birds

# Set default namespace
kubectl config set-context --current --namespace=miracle-birds

# Create secrets from AWS Secrets Manager
kubectl create secret generic miracle-birds-secrets \
  --from-literal=database-url="postgresql://user:pass@rds-endpoint:5432/miracle_birds" \
  --from-literal=redis-url="rediss://redis-endpoint:6379" \
  --from-literal=jwt-secret="$(openssl rand -hex 64)" \
  --from-literal=openai-api-key="your_openai_key"
```

### Install Ingress Controller

```bash
# Install NGINX Ingress Controller
helm repo add ingress-nginx https://kubernetes.github.io/ingress-nginx
helm repo update

helm install ingress-nginx ingress-nginx/ingress-nginx \
  --namespace ingress-nginx \
  --create-namespace \
  --set controller.replicaCount=2 \
  --set controller.nodeSelector."kubernetes.io/os"=linux \
  --set controller.service.type=LoadBalancer
```

### Install cert-manager (TLS)

```bash
helm repo add jetstack https://charts.jetstack.io
helm repo update

helm install cert-manager jetstack/cert-manager \
  --namespace cert-manager \
  --create-namespace \
  --version v1.13.0 \
  --set installCRDs=true
```

### Deploy Services

```bash
# Apply all Kubernetes manifests
kubectl apply -f infrastructure/kubernetes/base/

# Verify deployments
kubectl get deployments
kubectl get pods
kubectl get services
kubectl get ingress

# Check deployment status
kubectl rollout status deployment/miracle-birds-backend
kubectl rollout status deployment/miracle-birds-frontend
```

### Useful kubectl Commands

```bash
# View logs
kubectl logs -f deployment/miracle-birds-backend
kubectl logs -f deployment/miracle-birds-frontend

# Scale manually
kubectl scale deployment miracle-birds-backend --replicas=5

# Execute into pod
kubectl exec -it deployment/miracle-birds-backend -- /bin/bash

# Port forward for local testing
kubectl port-forward svc/miracle-birds-backend 8000:8000

# View resource usage
kubectl top pods
kubectl top nodes

# Describe pod (for debugging)
kubectl describe pod <pod-name>

# View events
kubectl get events --sort-by='.lastTimestamp'
```

---

## CI/CD Pipeline

### Overview

```
Developer pushes code
        │
        ▼
GitHub Actions triggered
        │
   ┌────┴────┐
   │         │
Backend   Frontend
Tests      Tests
   │         │
   └────┬────┘
        │
   Security Scan
   (Trivy + CodeQL)
        │
   Build Docker Images
   Push to GHCR
        │
   Deploy to Kubernetes
   (kubectl rollout)
        │
   Verify deployment
   Health checks
        │
   Notify Slack
```

### Required GitHub Secrets

Configure these in your GitHub repository settings:

```
AWS_ACCESS_KEY_ID       - AWS access key for deployment
AWS_SECRET_ACCESS_KEY   - AWS secret key for deployment
SLACK_WEBHOOK           - Slack webhook for notifications
```

### Branch Strategy

```
main        → Production deployment (auto)
develop     → Staging deployment (auto)
feature/*   → Tests only (no deployment)
hotfix/*    → Tests + production (with approval)
```

### Deployment Flow

```bash
# Feature development
git checkout -b feature/my-feature
git push origin feature/my-feature
# → Runs: tests + security scan

# Merge to develop
git checkout develop
git merge feature/my-feature
git push origin develop
# → Runs: tests + security scan + staging deploy

# Merge to main
git checkout main
git merge develop
git push origin main
# → Runs: tests + security scan + build + production deploy
```

### Rollback Procedure

```bash
# View rollout history
kubectl rollout history deployment/miracle-birds-backend

# Rollback to previous version
kubectl rollout undo deployment/miracle-birds-backend

# Rollback to specific version
kubectl rollout undo deployment/miracle-birds-backend --to-revision=3

# Verify rollback
kubectl rollout status deployment/miracle-birds-backend
kubectl get pods
```

---

## Monitoring Stack

### Install Prometheus & Grafana

```bash
# Add Prometheus community Helm repo
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo add grafana https://grafana.github.io/helm-charts
helm repo update

# Install kube-prometheus-stack (Prometheus + Grafana + Alertmanager)
helm install monitoring prometheus-community/kube-prometheus-stack \
  --namespace monitoring \
  --create-namespace \
  --set grafana.adminPassword="secure-grafana-password" \
  --set prometheus.prometheusSpec.retention=30d

# Apply custom Prometheus config
kubectl apply -f infrastructure/monitoring/prometheus/

# Access Grafana (port-forward)
kubectl port-forward -n monitoring svc/monitoring-grafana 3001:80
# Open http://localhost:3001 (admin / your-password)
```

### Key Dashboards

```
1. Miracle Birds Overview
   - API request rate
   - Error rate
   - Latency (P50, P95, P99)
   - Active users

2. AI/ML Metrics
   - Predictions per minute
   - Model inference latency
   - LLM token usage
   - Accuracy metrics

3. Infrastructure
   - CPU/Memory usage
   - Pod status
   - Node health
   - Database connections

4. Business Metrics
   - Customers synced
   - Churn predictions made
   - CRM sync status
   - API usage by tenant
```

### Alerting Channels

```bash
# Configure Alertmanager for Slack notifications
cat > alertmanager-config.yaml <<EOF
global:
  resolve_timeout: 5m

route:
  group_by: ['alertname', 'severity']
  group_wait: 10s
  group_interval: 10s
  repeat_interval: 1h
  receiver: 'slack-notifications'

receivers:
- name: 'slack-notifications'
  slack_configs:
  - api_url: 'https://hooks.slack.com/services/YOUR_WEBHOOK'
    channel: '#alerts'
    send_resolved: true
    title: '{{ .GroupLabels.alertname }}'
    text: '{{ .CommonAnnotations.summary }}'
EOF

kubectl apply -f alertmanager-config.yaml
```

---

## Scaling Strategy

### Horizontal Pod Autoscaling (HPA)

Already configured in manifests. Additional tuning:

```bash
# View HPA status
kubectl get hpa

# Manual test scaling
kubectl autoscale deployment miracle-birds-backend \
  --cpu-percent=70 \
  --min=3 \
  --max=10
```

### Cluster Autoscaler

```bash
# Install Cluster Autoscaler for EKS
helm repo add autoscaler https://kubernetes.github.io/autoscaler

helm install cluster-autoscaler autoscaler/cluster-autoscaler \
  --namespace kube-system \
  --set autoDiscovery.clusterName=miracle-birds-production \
  --set awsRegion=us-east-1
```

### Database Scaling

```bash
# Scale RDS vertically (requires brief downtime)
aws rds modify-db-instance \
  --db-instance-identifier miracle-birds-production \
  --db-instance-class db.r6g.2xlarge \
  --apply-immediately

# Add read replicas for read scaling
aws rds create-db-instance-read-replica \
  --db-instance-identifier miracle-birds-prod-read-1 \
  --source-db-instance-identifier miracle-birds-production
```

---

## Disaster Recovery

### Backup Strategy

```
Database (RDS):
├── Automated daily backups (30-day retention)
├── Point-in-time recovery (PITR) - last 35 days
└── Manual snapshots before major changes

Redis:
├── RDB snapshots every hour
└── 7-day snapshot retention

Application:
├── Docker images in GHCR (versioned)
├── Kubernetes manifests in Git
└── Terraform state in S3 (versioned)
```

### Recovery Procedures

```bash
# Database recovery from snapshot
aws rds restore-db-instance-from-db-snapshot \
  --db-instance-identifier miracle-birds-recovery \
  --db-snapshot-identifier miracle-birds-production-2026-07-13

# Point-in-time recovery
aws rds restore-db-instance-to-point-in-time \
  --source-db-instance-identifier miracle-birds-production \
  --target-db-instance-identifier miracle-birds-recovery \
  --restore-time 2026-07-13T18:00:00Z

# Kubernetes disaster recovery - redeploy everything
kubectl apply -f infrastructure/kubernetes/base/
kubectl rollout restart deployment --all
```

### RTO/RPO Targets

```
Recovery Time Objective (RTO):  < 1 hour
Recovery Point Objective (RPO): < 15 minutes

Tier 1 (Critical):
- Database: RPO 15 min, RTO 30 min (Multi-AZ failover)
- API: RPO 0 (stateless), RTO 5 min (pod restart)

Tier 2 (Important):
- ML Models: RPO 1 hour, RTO 15 min (S3 restore)
- CRM Sync: RPO 1 hour, RTO 30 min (restart job)
```

---

## Environment Variables Reference

```bash
# Backend
DATABASE_URL=postgresql://user:pass@host:5432/miracle_birds
REDIS_URL=rediss://user:pass@host:6379/0
JWT_SECRET=your-256-bit-secret
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
OPENAI_API_KEY=sk-...
GEMINI_API_KEY=...
ENVIRONMENT=production
LOG_LEVEL=INFO
ALLOWED_ORIGINS=https://miraclebirds.ai

# Frontend
NEXT_PUBLIC_API_URL=https://api.miraclebirds.ai
NEXT_PUBLIC_APP_URL=https://miraclebirds.ai
NODE_ENV=production
```

---

**Version:** 1.0  
**Last Updated:** July 13, 2026  
**Maintained by:** Miracle Birds DevOps Team
