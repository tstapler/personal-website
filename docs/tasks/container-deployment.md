# Container Deployment Strategy

## Objective
Implement comprehensive health checks and deployment strategies for the containerized personal website to ensure high availability and automatic rollback capabilities.

## Prerequisites
- Access to Kubernetes cluster configuration
- Docker build pipeline access
- Understanding of Kubernetes liveness/readiness probes
- `kubectl` configured for the target cluster

## Atomic Tasks

### Task 1: Health Check Implementation
**Priority**: High | **Size**: Small (2 hours) | **Context**: 3-4 files

**Objective**: Add application-level health check endpoints and configure Kubernetes probes.

**Files Required**:
- `deployment/personal-website/personal-site.yaml` (deployment config)
- `deployment/personal-website/files/nginx.conf` (nginx config for health endpoint)
- `Dockerfile` (if needed for health check script)

**Implementation Steps**:
1. Configure Nginx to serve a lightweight `/healthz` endpoint
2. Update Kubernetes Deployment YAML to include `livenessProbe`
3. Update Kubernetes Deployment YAML to include `readinessProbe`
4. Configure appropriate initialDelaySeconds, periodSeconds, and failureThreshold

**Validation**:
- Deploy to test environment
- Verify `/healthz` returns 200 OK
- Simulate failure (return 500) and verify pod restart (liveness)
- Simulate failure and verify traffic stop (readiness)

**Completion Criteria**: Kubernetes pods automatically restart on failure and remove themselves from service when unhealthy.

---

### Task 2: Rollback Strategy Configuration
**Priority**: Medium | **Size**: Small (1-2 hours) | **Context**: 2-3 files

**Objective**: Configure deployment strategy to ensure zero-downtime updates and automatic rollbacks.

**Files Required**:
- `deployment/personal-website/personal-site.yaml`

**Implementation Steps**:
1. Configure `strategy.type: RollingUpdate`
2. Set `maxUnavailable` and `maxSurge` parameters
3. Define `minReadySeconds` to ensure pod stability before progression
4. Document rollback commands (`kubectl rollout undo`)

**Validation**:
- Perform a rolling update
- Verify zero downtime during update
- Deploy a broken image (failing readiness)
- Verify rollout pauses/fails safely without taking down the site

**Completion Criteria**: Deployments are safe, zero-downtime, and automatically pause if new pods are unhealthy.

---

## Dependencies

### Sequential Dependencies
1. **Task 1** (Health Checks) is a prerequisite for effective **Task 2** (Rollback Strategy), as rollbacks rely on health status.

### Blocking Factors
- None identified.

## Context Preparation Notes

### For Task 1 (Health Checks)
- Review Nginx `stub_status` module or simple static file serving for health.
- Check `deployment/personal-website/personal-site.yaml` for current container spec.

### For Task 2 (Rollback Strategy)
- Understand Kubernetes Deployment strategies.
- Review current replica count in `personal-site.yaml`.

## Links

- **Main TODO**: [../../TODO.md](../../TODO.md)
- **Deployment Files**: [../../deployment/personal-website/](../../deployment/personal-website/)
