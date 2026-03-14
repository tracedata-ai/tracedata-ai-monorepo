# ADR 006: AWS ECS Fargate for TraceData Deployment

## Status
Proposed

## Context
TraceData requires a scalable, secure, and low-maintenance infrastructure to support its multi-agent AI middleware (FastAPI), frontend (Next.js), and background workers (Celery). 

The initial exploration considered traditional EC2 instances, but the operational overhead of patching, scaling logic, and OS management was deemed a bottleneck for rapid iteration.

## Decision
We will use **AWS ECS Fargate** (serverless containers) for the entire compute layer.

## Rationale
- **Zero Server Management**: No need to manage or patch underlying EC2 instances. AWS handles the infrastructure.
- **Isolation & Security**: Each task runs in its own isolated compute environment. Worker tasks are placed in private subnets with no public IP exposure.
- **Seamless Scaling**: ECS handles horizontal scaling based on CPU/Memory metrics without managing Auto Scaling Groups for EC2.
- **Cost Efficiency**: Pay-per-task execution (CPU/Memory) is ideal for our modular architecture where different services (Frontend vs. Worker) have different load profiles.
- **Deployment Safety**: Native support for Rolling Updates and health check integration with ALBs.

## Compliance & Performance
- **Database**: Amazon RDS (PostgreSQL) ensures data durability and automated backups.
- **Caching**: Amazon ElastiCache (Redis) provides high-throughput message brokerage for Celery.
- **Networking**: VPC isolation ensures that internal AI reasoning and sensitive driver data are never exposed to the public internet.

## Consequences
- **Positive**: Reduced operational burden; improved security posture; faster CI/CD cycles.
- **Negative**: Slightly higher hourly cost than reserved EC2; troubleshooting requires `aws ecs execute-command` rather than standard SSH.
