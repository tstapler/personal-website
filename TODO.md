# Personal Website TODOs

## Technical Tasks

### Web Design & User Experience
- [x] Fix summary overflow issues on summary page (HIGH PRIORITY)
  - **Bug**: [docs/bugs/fixed/summary-overflow.md](docs/bugs/fixed/summary-overflow.md)
  - **Task**: [docs/tasks/web-improvements.md#task-1-summary-overflow-bug-fix](docs/tasks/web-improvements.md#task-1-summary-overflow-bug-fix)
  - **Impact**: Critical user experience issue affecting blog listing pages
  - **Status**: ✅ COMPLETED 2025-01-02

- [x] Implement AI-generated blog post summaries
  - **Task**: [docs/tasks/ai-summary-implementation.md](docs/tasks/ai-summary-implementation.md)
  - **Dependencies**: Summary overflow bug fix required first
  - **Features**: Summary generation, quality testing, template integration
  - **Status**: ✅ COMPLETED 2025-01-10

- [x] **Feature: Cloudflare Deployment** <!-- id: cloudflare-deployment -->
  - **Task**: [docs/tasks/cloudflare-deployment.md](docs/tasks/cloudflare-deployment.md)
  - **Goal**: Migrate to Cloudflare Pages for edge performance
  - **Status**: ✅ COMPLETED
  - **Subtasks**:
    - [x] Task 1.1: Create Cloudflare Workflow (`.github/workflows/cloudflare.yml`)
    - [x] Task 2.1: Configure Wrangler (`wrangler.toml`)
    - [x] Task 3.1: Documentation & Cleanup (`README.md`, `ARCHITECTURE.md`)

### Infrastructure & Deployment
- [x] Container Deployment Strategy
  - **Task**: [docs/tasks/container-deployment.md](docs/tasks/container-deployment.md)
  - **Features**: Health checks, rollback detection, blue-green deployment
  - **Documentation**: Implementation process for blog post
  - **Note**: Auto-updates will be implemented in separate monitoring repo
  - **Status**: ✅ COMPLETED 2025-01-11

- [ ] ArgoCD Integration
  - **Task**: [docs/tasks/argocd-integration.md](docs/tasks/argocd-integration.md)
  - **Goal**: Implement GitOps for automated cluster state management
  - **Status**: 🚧 IN PROGRESS
  - **Subtasks**:
    - [x] Task 1.1: Install ArgoCD
    - [ ] Task 1.2: Configure Access & CLI
    - [x] Task 2.1: Create Website Application Manifest

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
