# Personal Website TODOs

## Technical Tasks

### Web Design & User Experience
- [ ] Fix summary overflow issues on summary page (HIGH PRIORITY)
  - **Bug**: [docs/bugs/open/summary-overflow.md](docs/bugs/open/summary-overflow.md)
  - **Task**: [docs/tasks/web-improvements.md#task-1-summary-overflow-bug-fix](docs/tasks/web-improvements.md#task-1-summary-overflow-bug-fix)
  - **Impact**: Critical user experience issue affecting blog listing pages

- [ ] Implement AI-generated blog post summaries
  - **Task**: [docs/tasks/web-improvements.md#task-2-ai-generated-blog-summaries](docs/tasks/web-improvements.md#task-2-ai-generated-blog-summaries)
  - **Dependencies**: Summary overflow bug fix required first
  - **Features**: Summary generation, quality testing, template integration

### Infrastructure & Deployment
- [ ] Container Deployment Strategy
  - **Task**: [docs/tasks/web-improvements.md#task-3-container-deployment-health-checks](docs/tasks/web-improvements.md#task-3-container-deployment-health-checks)
  - **Features**: Health checks, rollback detection, blue-green deployment
  - **Documentation**: Implementation process for blog post
  - **Note**: Auto-updates will be implemented in separate monitoring repo

- [ ] ArgoCD Integration
  - Install and configure ArgoCD in kubernetes cluster
  - Setup GitOps workflow
  - Document setup process and benefits for blog

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
  - Performance impact and benefits

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

## Infrastructure Improvements
- [ ] Container Deployment Strategy
  - Implement health checks for rollback detection
  - Configure blue-green deployment strategy
  - Document implementation process for blog
  - Note: Auto-updates will be implemented in separate monitoring repo

- [ ] ArgoCD Integration
  - Install and configure ArgoCD in kubernetes cluster
  - Setup GitOps workflow
  - Document setup process and benefits for blog

## Web Design
- [ ] Bug Fixes
  - Fix summary overflow issues on summary page
  
- [ ] New Features
  - Implement AI-generated blog post summaries
  - Test summary generation quality
  - Add summary display to blog template
