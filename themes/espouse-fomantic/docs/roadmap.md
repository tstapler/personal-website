# Espouse Theme Roadmap

## Executive Summary

Espouse is a Hugo theme built on Semantic UI 2.4.2 with webpack-based build system. This roadmap addresses critical technical debt, security vulnerabilities, and feature enhancements to modernize the theme for 2025 and beyond.

**Current State:**
- 230MB node_modules with 29+ outdated packages
- Webpack 4.x with deprecated tooling (node-sass, Gulp 3.x)
- Recent template pagination bugs (partially fixed)
- Dark mode planned but not implemented
- jQuery 3.5.1 with known security patches available

## Phase 1: Critical Updates & Security (IMMEDIATE - Weeks 1-4)

**Priority Level:** CRITICAL
**Estimated Effort:** 12-16 hours
**Value:** Security compliance, stability, build reliability

### 1.1 Security Audit & Dependency Updates

**Objective:** Eliminate known vulnerabilities and update packages with security patches

**Tasks:**
1. Run comprehensive security audit
2. Update jQuery 3.5.1 → 3.7.1 (security patches)
3. Update Semantic UI 2.4.2 → 2.5.0
4. Resolve critical/high severity npm vulnerabilities
5. Update Babel toolchain (@babel/core 7.11.4 → 7.28.5)

**Success Criteria:**
- Zero critical/high npm audit findings
- All security patches applied
- Build passes successfully

**Context Boundary:** package.json, package-lock.json, webpack.config.js (3 files)

### 1.2 Build Toolchain Modernization

**Objective:** Replace deprecated tools with modern alternatives

**Tasks:**
1. Replace node-sass 4.14.1 with sass (Dart Sass) 1.x
2. Update sass-loader 9.0.3 → 16.0.6 (compatible with Dart Sass)
3. Migrate Gulp 3.9.1 → 5.0.1 (breaking changes)
4. Update gulpfile.js for Gulp 5 API changes
5. Test Semantic UI build process with new toolchain

**Success Criteria:**
- Successful builds with Dart Sass
- Gulp 5 tasks functioning
- No deprecation warnings

**Context Boundary:** package.json, gulpfile.js, semantic.json (3 files)

### 1.3 Template Bug Fixes

**Objective:** Complete pagination fixes and add validation

**Tasks:**
1. Verify all pagination template fixes are complete
2. Add template validation for all page types
3. Test homepage, list pages, single pages, photography sections
4. Add error boundary templates

**Success Criteria:**
- No template execution errors
- All page types render correctly
- Graceful error handling

**Context Boundary:** layouts/partials/meta.html, layouts/_default/list.html (2 files)

## Phase 2: Build System Modernization (SHORT-TERM - Months 2-3)

**Priority Level:** HIGH
**Estimated Effort:** 20-24 hours
**Value:** Developer experience, build performance, maintainability

### 2.1 Webpack 5 Migration

**Objective:** Modernize webpack configuration for improved performance

**Tasks:**
1. Update webpack 4.44.1 → 5.x (latest stable)
2. Update webpack-cli 3.3.10 → 5.x
3. Migrate deprecated plugins (OccurrenceOrderPlugin removed)
4. Update mini-css-extract-plugin 0.10.0 → 2.9.4
5. Configure persistent caching for faster rebuilds
6. Update terser-webpack-plugin for better minification

**Success Criteria:**
- Successful webpack 5 builds
- Faster rebuild times (target 30% improvement)
- Smaller bundle sizes

**Context Boundary:** webpack.config.js, package.json (2 files)

### 2.2 Performance Optimization

**Objective:** Reduce bundle sizes and improve load times

**Tasks:**
1. Implement lazy loading for particles.js (homepage only)
2. Add bundle analysis and size monitoring
3. Optimize image assets (SVG optimization)
4. Implement tree-shaking for unused code
5. Split vendor bundles appropriately

**Success Criteria:**
- 30-50% reduction in JavaScript bundle size
- particles.js only loads on homepage
- Lighthouse performance score 90+

**Context Boundary:** webpack.config.js, app.js, src/homePage.js (3 files)

### 2.3 CSS Pipeline Modernization

**Objective:** Modernize CSS processing and reduce output size

**Tasks:**
1. Update cssnano 4.1.10 → 7.1.2
2. Update css-minimizer-webpack-plugin 1.1.2 → 7.0.2
3. Implement modern PostCSS pipeline
4. Add critical CSS extraction
5. Optimize Semantic UI customization

**Success Criteria:**
- Smaller CSS bundles
- Faster CSS processing
- Critical CSS inline for faster FCP

**Context Boundary:** webpack.config.js, src/semantic.less (2 files)

## Phase 3: Feature Enhancements (MEDIUM-TERM - Months 3-4)

**Priority Level:** MEDIUM
**Estimated Effort:** 16-20 hours
**Value:** User experience, accessibility, modern features

### 3.1 Dark Mode Implementation

**Objective:** Implement complete dark mode with user preference persistence

**Tasks (already outlined in TODO.md):**
1. Create CSS custom properties foundation
2. Implement dark mode class override
3. Add theme toggle UI component
4. Create theme manager JavaScript class
5. Add localStorage persistence
6. Implement system preference detection
7. Ensure WCAG contrast compliance

**Success Criteria:**
- Functional dark/light mode toggle
- Preference persistence across sessions
- System preference detection working
- WCAG AA contrast compliance

**Context Boundary:** sass/espouse.scss, src/espouse.js, layouts/partials/header.html (3 files)

### 3.2 Accessibility Audit & Improvements

**Objective:** Achieve WCAG 2.1 AA compliance

**Tasks:**
1. Run automated accessibility audit (Lighthouse, axe)
2. Add missing ARIA labels
3. Improve keyboard navigation
4. Ensure color contrast compliance
5. Add skip-to-content links
6. Test with screen readers

**Success Criteria:**
- Lighthouse accessibility score 95+
- Zero critical/serious axe violations
- Full keyboard navigation support

**Context Boundary:** layouts/partials/*.html (3-5 files)

### 3.3 Progressive Web App Features

**Objective:** Add PWA capabilities for offline support

**Tasks:**
1. Create web app manifest
2. Implement service worker
3. Add cache strategies for assets
4. Enable installability
5. Add offline fallback page

**Success Criteria:**
- PWA lighthouse audit passes
- Installable from browser
- Basic offline functionality

**Context Boundary:** static/manifest.json, static/sw.js (2 files, new)

## Phase 4: Modernization & Optimization (LONG-TERM - Months 5-6)

**Priority Level:** LOW
**Estimated Effort:** 24-32 hours
**Value:** Code quality, maintainability, future-proofing

### 4.1 JavaScript Modernization

**Objective:** Reduce/eliminate jQuery dependency

**Tasks:**
1. Audit jQuery usage across codebase
2. Replace simple jQuery calls with vanilla JS
3. Modernize event handling
4. Use native DOM APIs
5. Implement modern module system

**Success Criteria:**
- jQuery removed from non-Semantic UI code
- Smaller JavaScript bundles
- Modern ES6+ patterns throughout

**Context Boundary:** src/*.js files (3-4 files)

### 4.2 CSS Modernization

**Objective:** Leverage modern CSS features

**Tasks:**
1. Implement CSS custom properties throughout
2. Use CSS Grid where appropriate
3. Reduce Semantic UI overrides
4. Implement modern layout techniques
5. Add container queries for responsive design

**Success Criteria:**
- Cleaner CSS architecture
- Reduced override complexity
- Better maintainability

**Context Boundary:** sass/espouse.scss, src/site/*.less (3-5 files)

### 4.3 Asset Optimization

**Objective:** Modernize asset handling and formats

**Tasks:**
1. Implement SVG sprite system
2. Add WebP/AVIF image support
3. Optimize font loading
4. Add resource hints (preconnect, prefetch)
5. Implement responsive images

**Success Criteria:**
- Faster asset loading
- Modern image formats supported
- Optimized font delivery

**Context Boundary:** webpack.config.js, layouts/partials/html_head.html (2 files)

## Phase 5: Developer Experience (ONGOING)

**Priority Level:** MEDIUM
**Estimated Effort:** 12-16 hours
**Value:** Maintainability, collaboration, code quality

### 5.1 Documentation

**Tasks:**
1. Complete theme customization guide
2. Document all configuration options
3. Add JSDoc comments to JavaScript
4. Create contribution guidelines
5. Document build process

**Success Criteria:**
- Comprehensive documentation
- Easy onboarding for contributors
- Clear customization examples

### 5.2 Testing Infrastructure

**Tasks:**
1. Add HTML validation tests
2. Implement Lighthouse CI
3. Add visual regression testing
4. Create cross-browser test suite
5. Add pre-commit hooks

**Success Criteria:**
- Automated quality checks
- CI/CD pipeline
- Regression prevention

### 5.3 Tooling Improvements

**Tasks:**
1. Add Prettier for code formatting
2. Implement Husky for git hooks
3. Add commitlint for conventional commits
4. Create release automation
5. Add automated dependency updates

**Success Criteria:**
- Consistent code style
- Automated quality gates
- Streamlined release process

## Phase 6: Content & Feature Expansion (FUTURE)

**Priority Level:** LOW
**Estimated Effort:** Variable
**Value:** Feature completeness, versatility

### Additional Content Types
- Blog post layouts with enhanced typography
- Portfolio/project showcase templates
- Resume/CV template
- Contact form integration

### Enhanced Photography Features
- Gallery lightbox improvements
- Image lazy loading with blurhash placeholders
- EXIF data display
- Photography collections/albums

### Social & Sharing
- Enhanced social sharing buttons
- Expanded JSON-LD structured data
- Comment system integration
- Newsletter signup integration

## Implementation Strategy

### Immediate Actions (Next Sprint)
1. Security audit and critical updates (1.1)
2. node-sass → sass migration (1.2)
3. Complete template bug fixes (1.3)

### Short-term Goals (Months 1-2)
1. Webpack 5 migration (2.1)
2. Performance optimization (2.2)
3. Dark mode implementation (3.1)

### Medium-term Goals (Months 3-6)
1. Accessibility improvements (3.2)
2. PWA features (3.3)
3. JavaScript modernization (4.1)

### Ongoing Efforts
1. Documentation updates (5.1)
2. Testing infrastructure (5.2)
3. Tooling improvements (5.3)

## Success Metrics

**Performance:**
- Bundle size reduction: 30-50%
- Build time: <10 seconds
- Lighthouse scores: 95+ all categories

**Security:**
- Zero critical/high vulnerabilities
- Regular dependency updates
- Automated security scanning

**Quality:**
- WCAG 2.1 AA compliance
- Zero template errors
- Comprehensive test coverage

**Developer Experience:**
- Fast rebuild times (<2s)
- Clear documentation
- Automated workflows

## Risk Assessment

**High Risk:**
- Webpack 5 migration (breaking changes)
- Gulp 3 → 5 migration (API changes)
- jQuery removal from Semantic UI integration

**Medium Risk:**
- Dark mode CSS variable conflicts
- Performance regressions during modernization
- Build process complexity

**Low Risk:**
- Documentation updates
- Incremental dependency updates
- Accessibility improvements

## Dependencies & Constraints

**External Dependencies:**
- Semantic UI maintenance status (limited updates)
- Hugo compatibility requirements
- Browser support targets (last 2 versions)

**Technical Constraints:**
- Semantic UI requires jQuery (cannot fully remove)
- Webpack ecosystem maturity
- Hugo templating limitations

**Resource Constraints:**
- Solo developer effort
- No breaking changes to existing sites
- Backward compatibility preferred

## Next Steps

See `docs/tasks/phase1-critical-updates.md` for detailed atomic task breakdown of immediate priorities.
