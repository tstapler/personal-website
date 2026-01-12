# Feature Plan: ArgoCD Integration

## Epic Overview

**User Value**
Implementing ArgoCD enables a true GitOps workflow for the personal website and future cluster services. It provides a declarative source of truth for the cluster state, automated synchronization, and a visual dashboard for application health, replacing manual `kubectl apply` or Helm commands.

**Success Metrics**
- **Automation**: Zero manual `kubectl` commands required for deployment.
- **Visibility**: Real-time dashboard showing application sync status and health.
- **Reliability**: Automatic drift detection and self-healing (optional).
- **Security**: RBAC-controlled access to deployment operations.

**Scope**
- **Included**:
    - Installation of ArgoCD in the Kubernetes cluster.
    - Configuration of the personal website as an ArgoCD Application.
    - Documentation of the GitOps workflow.
- **Excluded**:
    - SSO integration (initial phase uses local admin).
    - Multi-cluster setup.

## Story Breakdown

### Story 1: Installation & Basic Configuration [1-2 days]
**User Value**: Establishes the GitOps control plane in the cluster.
**Acceptance Criteria**:
- ArgoCD pods are running and healthy in `argocd` namespace.
- ArgoCD CLI is installed locally (or instructions provided).
- Web UI is accessible via Ingress or Port-forwarding.
- Admin password is retrieved and login is successful.

### Story 2: Application Onboarding [1 day]
**User Value**: Migrates the personal website deployment to GitOps.
**Acceptance Criteria**:
- `Application` manifest created for the personal website.
- ArgoCD successfully syncs the Helm chart from the git repository.
- Website remains accessible during/after migration.

## Atomic Task Decomposition

### Task 1.1: Install ArgoCD
- **Objective**: Deploy ArgoCD to the Kubernetes cluster using Helm or Manifests.
- **Context Boundary**:
    - Files: `deployment/argocd/install.yaml` (or script), `deployment/argocd/values.yaml`.
    - Concepts: Kubernetes, Helm, ArgoCD.
- **Prerequisites**: `kubectl` access to the cluster.
- **Implementation Approach**:
    1.  Create `argocd` namespace.
    2.  Apply the stable ArgoCD install manifest or use the Helm chart.
    3.  Verify all pods are running.
- **Validation Strategy**:
    - `kubectl get pods -n argocd` shows all pods Running.
- **INVEST Check**: Independent, Valuable, Small (1h), Testable.
- **Status**: ⏳ Pending

### Task 1.2: Configure Access & CLI
- **Objective**: Establish access to the ArgoCD UI and CLI.
- **Context Boundary**:
    - Files: `deployment/argocd/ingress.yaml` (optional), `docs/operations/argocd.md`.
    - Concepts: Ingress, Port-forwarding, Secrets.
- **Prerequisites**: Task 1.1.
- **Implementation Approach**:
    1.  Retrieve initial admin password from secrets.
    2.  Set up port-forwarding or Ingress for the UI.
    3.  Login via CLI and UI.
- **Validation Strategy**:
    - Successful login to the ArgoCD web dashboard.
- **INVEST Check**: Independent, Valuable, Micro (1h), Testable.
- **Status**: ⏳ Pending

### Task 2.1: Create Website Application Manifest
- **Objective**: Define the personal website as an ArgoCD Application.
- **Context Boundary**:
    - Files: `deployment/argocd/applications/personal-website.yaml`.
    - Concepts: ArgoCD Application CRD.
- **Prerequisites**: Task 1.2.
- **Implementation Approach**:
    1.  Create an `Application` manifest pointing to the `deployment/personal-website` path in the repo.
    2.  Configure sync policy (manual first, then automated).
    3.  Apply the manifest.
- **Validation Strategy**:
    - App appears in ArgoCD UI.
    - Sync status becomes "Synced".
    - Health status becomes "Healthy".
- **INVEST Check**: Independent, Valuable, Small (1-2h), Testable.
- **Status**: ⏳ Pending

## Dependency Visualization

```
[Start]
   |
   +---> [Task 1.1: Install ArgoCD]
           |
           +---> [Task 1.2: Configure Access]
                   |
                   +---> [Task 2.1: Create Website App]
```

## Context Preparation Guide
- **Task 1.1**:
    - Review [ArgoCD Getting Started Guide](https://argo-cd.readthedocs.io/en/stable/getting_started/).
    - Check current cluster nodes/resources.

## Links
- **Main TODO**: [../../TODO.md](../../TODO.md)
- **ArgoCD Docs**: https://argo-cd.readthedocs.io/
