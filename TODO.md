# Personal Website TODOs

## Technical Tasks

### Web Design & User Experience

- [x] Fix summary overflow issues on summary page (HIGH PRIORITY)
  - **Bug**: [docs/bugs/fixed/summary-overflow.md](docs/bugs/fixed/summary-overflow.md)
  - **Status**: ✅ COMPLETED 2025-01-02

- [x] Implement AI-generated blog post summaries
  - **Task**: [docs/tasks/ai-summary-implementation.md](docs/tasks/ai-summary-implementation.md)
  - **Status**: ✅ COMPLETED 2025-01-10

- [x] **Feature: Cloudflare Deployment**
  - **Task**: [docs/tasks/cloudflare-deployment.md](docs/tasks/cloudflare-deployment.md)
  - **Status**: ✅ COMPLETED

- [x] **Site UX Overhaul + Pagefind Search** (shipped via PR #17)
  - Reading progress bar, copy-code buttons, heading anchors, TOC
  - Blog feed redesigned as vertical list with meta (date, tags, read-time)
  - particles.js replaced with canvas animation (saved 87 KB)
  - Accessibility: skip link, keyboard nav, focus styles, contrast fixes
  - Pagefind full-text search page + CI indexing step
  - CSS custom properties (color tokens) extracted to `site-enhancements.css`
  - **Status**: ✅ COMPLETED 2026-04-19

- [ ] **Dark Mode Token Overrides**
  - **Task**: [docs/tasks/dark-mode.md](docs/tasks/dark-mode.md)
  - **Goal**: Add `@media (prefers-color-scheme: dark)` block to espouse theme,
    overriding the 12 CSS custom properties already defined. No JS required.
  - **Status**: Pending
  - **Subtasks**:
    - [ ] Task 1.1: Add dark-mode token overrides to `site-enhancements.css` (2h)
    - [ ] Task 1.2: Bump espouse submodule pointer in parent repo (0.5h)

### Infrastructure & Deployment

- [x] Container Deployment Strategy
  - **Task**: [docs/tasks/container-deployment.md](docs/tasks/container-deployment.md)
  - **Status**: ✅ COMPLETED 2025-01-11

- [ ] ArgoCD Integration
  - **Task**: [docs/tasks/argocd-integration.md](docs/tasks/argocd-integration.md)
  - **Goal**: Implement GitOps for automated cluster state management
  - **Status**: IN PROGRESS
  - **Subtasks**:
    - [x] Task 1.1: Install ArgoCD
    - [x] Task 1.2: Configure Access & CLI
    - [x] Task 2.1: Create Website Application Manifest
    - [x] Task 2.2: Create ArgoCD Verification Script
    - [ ] Task 2.3: Document GitOps Workflow (1h)

## Content Planning

### Planned Blog Posts

### Home Lab & Networking
- [ ] Unifi Security Gateway Issues
  - Power surge problems and high-pitched whining
  - Bricked Cloud Key and SSD after long-term power removal
  - Self-hosting Unifi server on gaming desktop
  - NFT-related issues and solutions
  - Troubleshooting Bad hardware in building using vaping

### Infrastructure & Storage
- [ ] Git Annex Setup
  - Document mirroring strategy for important files
  - Backup locations and methodology

### VPN & Network Security
- [ ] Transitioning from Tinc to Tailscale
  - Migration process
  - Performance improvements with Wireguard
  - Network architecture changes

### Server & Hardware
- [ ] Supermicro Server Review
  - eBay purchase experience
  - IPMI VLAN setup
  - Hardware specifications and performance

### Storage & Networking
- [ ] Ceph Cluster Network Optimization
  - VLAN separation for control plane traffic
  - Performance impact and ben
efits

### Academic Experiences
- [ ] Iowa State Course Impact Review
  - ISU Hackathons/HackISU experiences
  - National Cyber Analyst Challenge participation
  - Linux Essentials course outcomes
  - Operating Systems course projects
  - Computer Organization/Design lessons
  - Cybersecurity course applications
  - Professional growth through coursework

### Hardware Reviews & Troubleshooting
- [ ] Printer & Scanner Adventures
  - Printer firmware downgrade via print job
  - Brother scanner Linux setup challenges

### Infrastructure Projects
- [ ] New Rack Build
  - Planning and implementation
  - 2025 KVM options investigation
  - Time investment and lessons learned
