# Architecture Documentation

## Deployment Strategy

### Cloudflare Pages Deployment
- **Edge Network**: Static content is served via Cloudflare's global edge network for low latency.
- **Build Pipeline**: Reuses the existing Bazel `//:site_optimized` target.
- **Parallel Deployment**: Runs alongside the Kubernetes deployment during the transition phase.
- **Preview Deployments**: Every Pull Request generates a unique preview URL for validation.

### Blue-Green Deployment
- Production and staging environments run in parallel
- Zero-downtime deployments through traffic switching
- Rollback capability by reverting traffic routing

### ArgoCD Integration
- GitOps-based deployment automation
- Application configuration as code
- Automated sync and drift detection

## System Components

### Infrastructure
- Kubernetes clusters for blue/green environments
- Load balancers for traffic management
- Monitoring and alerting setup

### Deployment Pipeline
1. CI builds and tests
2. Container image creation and scanning
3. ArgoCD sync to staging
4. Production promotion via traffic switch

## Future Considerations
- Scaling strategy
- Disaster recovery procedures
- Performance optimization plans
