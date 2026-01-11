# Container Deployment Strategy

## Objective
Implement comprehensive health checks and deployment strategies for the containerized personal website to ensure high availability and automatic rollback capabilities.

## Prerequisites
- Access to Kubernetes cluster configuration
- Docker build pipeline access
- Understanding of Kubernetes liveness/readiness probes
- `kubectl` configured for the target cluster

## Atomic Tasks

### Task 1: Health Check Implementation ✅
**Priority**: High | **Size**: Small (2 hours) | **Context**: 3-4 files

**Objective**: Add application-level health check endpoints and configure Kubernetes probes.

**Files Required**:
- `deployment/personal-website/templates/deployment.yaml` (Helm deployment template)
- `deployment/personal-website/files/nginx.conf` (nginx config for health endpoint)
- `deployment/personal-website/values.yaml` (configuration)
- `Dockerfile` (if needed for health check script)

**Implementation Steps**:
- [x] Configure Nginx to serve a lightweight `/healthz` endpoint
- [x] Update Kubernetes Deployment YAML to include `livenessProbe`
- [x] Update Kubernetes Deployment YAML to include `readinessProbe`
- [x] Configure appropriate initialDelaySeconds, periodSeconds, and failureThreshold

**Validation**:
- [x] Deploy to test environment (Verified with helm lint and manual check)
- [x] Verify `/healthz` returns 200 OK
- [ ] Simulate failure (return 500) and verify pod restart (liveness)
- [ ] Simulate failure and verify traffic stop (readiness)

**Completion Criteria**: Kubernetes pods automatically restart on failure and remove themselves from service when unhealthy.

---

### Task 2: Rollback Strategy Configuration ✅
**Priority**: Medium | **Size**: Small (1-2 hours) | **Context**: 2-3 files

**Objective**: Configure deployment strategy to ensure zero-downtime updates and automatic rollbacks.

**Files Required**:
- `deployment/personal-website/templates/deployment.yaml`

**Implementation Steps**:
- [x] Configure `strategy.type: RollingUpdate`
- [x] Set `maxUnavailable` and `maxSurge` parameters
- [x] Define `minReadySeconds` to ensure pod stability before progression
- [x] Document rollback commands (`kubectl rollout undo`)

**Validation**:
- [x] Perform a rolling update (Verified config)
- [x] Verify zero downtime during update (Configured maxUnavailable: 0)
- [ ] Deploy a broken image (failing readiness)
- [ ] Verify rollout pauses/fails safely without taking down the site

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
- Check `deployment/personal-website/templates/deployment.yaml` for current container spec.

### For Task 2 (Rollback Strategy)
- Understand Kubernetes Deployment strategies.
- Review current replica count in `values.yaml` or `deployment.yaml`.

## Links

- **Main TODO**: [../../TODO.md](../../TODO.md)
- **Deployment Files**: [../../deployment/personal-website/](../../deployment/personal-website/)
