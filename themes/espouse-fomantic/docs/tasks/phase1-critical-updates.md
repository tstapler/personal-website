# Phase 1: Critical Updates & Security - Atomic Task Breakdown

## Overview

**Phase Goal:** Eliminate security vulnerabilities, modernize deprecated tooling, and ensure build stability
**Total Estimated Effort:** 12-16 hours
**Priority:** CRITICAL
**Context Boundary:** 3-5 files per task, 1-4 hours per task

## Task Dependency Graph

```
┌─────────────────────────────────┐
│ Task 1.1: Security Audit        │ (1-2h) - START HERE
└──────────────┬──────────────────┘
               │
               ▼
┌─────────────────────────────────┐
│ Task 1.2: jQuery Update         │ (1h) - Independent
└─────────────────────────────────┘

┌─────────────────────────────────┐
│ Task 1.3: Babel Toolchain Update│ (1-2h) - Independent
└─────────────────────────────────┘

┌─────────────────────────────────┐
│ Task 1.4: node-sass → sass      │ (2-3h) - BLOCKS 1.5
└──────────────┬──────────────────┘
               │
               ▼
┌─────────────────────────────────┐
│ Task 1.5: Gulp 3 → 5 Migration  │ (3-4h) - DEPENDS ON 1.4
└─────────────────────────────────┘

┌─────────────────────────────────┐
│ Task 1.6: Template Bug Fixes    │ (2h) - Independent
└─────────────────────────────────┘

┌─────────────────────────────────┐
│ Task 1.7: Final Integration Test│ (1h) - AFTER ALL
└─────────────────────────────────┘
```

## Task 1.1: Security Audit & Critical Vulnerability Resolution

**Objective:** Identify and resolve all critical/high severity npm vulnerabilities

**Size:** Small (1-2 hours)
**Priority:** CRITICAL (MUST DO FIRST)
**Context Boundary:** 2 files

**Prerequisites:**
- Current working build
- Access to npm audit

**Files Required:**
1. `package.json` (primary)
2. `package-lock.json` (supporting)

**Atomic Steps:**
1. Run `npm audit` and capture full output
2. Run `npm audit --json > docs/security-audit.json` for reference
3. Identify all CRITICAL and HIGH severity vulnerabilities
4. For each critical/high vulnerability:
   - Document CVE details
   - Determine if fix available
   - Test fix in isolation
5. Apply fixes using `npm audit fix` where safe
6. Manually update packages requiring breaking changes
7. Verify build still works after each fix

**Success Criteria:**
- [ ] Zero CRITICAL severity vulnerabilities
- [ ] Zero HIGH severity vulnerabilities
- [ ] Build passes: `npm run build` succeeds
- [ ] Security audit report saved to docs/
- [ ] All changes documented in commit message

**Validation:**
```bash
npm audit --production
npm run build
npm test
```

**Expected Output:**
- Clean npm audit (0 critical, 0 high)
- docs/security-audit-YYYY-MM-DD.json created
- Updated package.json and package-lock.json

**Rollback Plan:**
- Git revert if build fails
- Restore package-lock.json from backup

---

## Task 1.2: jQuery Security Update

**Objective:** Update jQuery from 3.5.1 to 3.7.1 for security patches

**Size:** Micro (1 hour)
**Priority:** HIGH
**Context Boundary:** 2 files

**Prerequisites:**
- Task 1.1 completed (audit done)

**Files Required:**
1. `package.json` (primary)
2. `webpack.config.js` (verification)

**Atomic Steps:**
1. Document current jQuery version and usage
2. Review jQuery 3.7.1 changelog for breaking changes
3. Update package.json: `"jquery": "^3.7.1"`
4. Run `npm install`
5. Test all jQuery-dependent functionality:
   - Semantic UI components
   - Table styling (src/espouse.js)
   - Homepage particles integration
6. Run production build
7. Verify no console errors

**Success Criteria:**
- [ ] jQuery updated to 3.7.1
- [ ] No breaking changes detected
- [ ] All interactive components work
- [ ] Production build succeeds
- [ ] No new console warnings/errors

**Validation:**
```bash
npm list jquery
npm run build
# Manual: Test site in browser
```

**Testing Checklist:**
- [ ] Semantic UI dropdowns work
- [ ] Table styling applies correctly
- [ ] Homepage particles render
- [ ] No console errors in DevTools

---

## Task 1.3: Babel Toolchain Update

**Objective:** Update Babel core and presets to latest 7.x versions

**Size:** Small (1-2 hours)
**Priority:** HIGH
**Context Boundary:** 3 files

**Prerequisites:**
- Task 1.1 completed

**Files Required:**
1. `package.json` (primary)
2. `webpack.config.js` (configuration)
3. `.babelrc` or babel config (if exists)

**Atomic Steps:**
1. Document current Babel versions
2. Update @babel/core: 7.11.4 → 7.28.5
3. Update @babel/preset-env: 7.11.0 → 7.28.5
4. Update babel-loader: 8.1.0 → 8.4.1
5. Check for breaking changes in changelog
6. Update babel configuration if needed
7. Test transpilation on sample ES6+ code
8. Run full build and verify output
9. Check bundle sizes (should be similar or smaller)

**Success Criteria:**
- [ ] All Babel packages at 7.28.5
- [ ] babel-loader at 8.4.1
- [ ] No transpilation errors
- [ ] Production build succeeds
- [ ] Bundle sizes unchanged or improved

**Validation:**
```bash
npm list @babel/core @babel/preset-env babel-loader
npm run build
# Compare bundle sizes before/after
ls -lh static/js/
```

**Risk Assessment:**
- Low risk: Babel 7.x series maintains backward compatibility
- Mitigation: Test builds incrementally

---

## Task 1.4: Replace node-sass with Dart Sass

**Objective:** Migrate from deprecated node-sass to modern sass (Dart Sass)

**Size:** Medium (2-3 hours)
**Priority:** CRITICAL (BLOCKS Task 1.5)
**Context Boundary:** 4 files

**Prerequisites:**
- Task 1.1 completed
- Understanding of current Sass compilation

**Files Required:**
1. `package.json` (primary)
2. `webpack.config.js` (sass-loader config)
3. `gulpfile.js` (gulp-sass config)
4. `sass/espouse.scss` (test compilation)

**Atomic Steps:**
1. Document current node-sass usage and version
2. Remove node-sass from package.json
3. Add sass (Dart Sass): `npm install --save-dev sass@^1.0.0`
4. Update sass-loader: 9.0.3 → 16.0.6
5. Update webpack.config.js sass-loader configuration:
   ```js
   {
     test: /\.scss$/,
     use: [
       MiniCssExtractPlugin.loader,
       'css-loader',
       {
         loader: 'sass-loader',
         options: {
           implementation: require('sass'),
           sassOptions: {
             // Add any required options
           }
         }
       },
       'resolve-url-loader'
     ]
   }
   ```
6. Update gulp-sass configuration in gulpfile.js:
   ```js
   const sass = require('gulp-sass')(require('sass'));
   ```
7. Test Sass compilation:
   ```bash
   npm run build
   ```
8. Verify compiled CSS is identical or improved
9. Check for any deprecation warnings
10. Test Semantic UI build process

**Success Criteria:**
- [ ] node-sass removed from dependencies
- [ ] sass (Dart Sass) installed and working
- [ ] sass-loader updated to 16.0.6
- [ ] Webpack build succeeds
- [ ] Gulp build succeeds
- [ ] CSS output is correct
- [ ] No compilation errors or warnings

**Validation:**
```bash
npm list node-sass  # Should show "empty"
npm list sass       # Should show sass@1.x
npm run build
make build-semantic
# Compare CSS output before/after
diff <(old-css) <(new-css)
```

**Known Issues & Mitigations:**
- Dart Sass has slightly different behavior than node-sass
- Some @import paths may need adjustment
- Division operator changed from `/` to `math.div()`
- Mitigation: Test thoroughly, check Sass deprecation warnings

**Rollback Plan:**
- Keep node-sass in git history
- Revert commits if critical issues found

---

## Task 1.5: Gulp 3.x → 5.x Migration

**Objective:** Update Gulp from deprecated 3.9.1 to modern 5.0.1

**Size:** Large (3-4 hours)
**Priority:** HIGH (DEPENDS ON Task 1.4)
**Context Boundary:** 3 files

**Prerequisites:**
- Task 1.4 completed (Dart Sass working)
- Gulp 3 currently functional

**Files Required:**
1. `package.json` (primary)
2. `gulpfile.js` (primary - major changes)
3. `semantic.json` (Semantic UI config)

**Breaking Changes to Address:**
- Task function signatures changed
- Series/parallel execution required
- Stream handling differences
- Plugin compatibility

**Atomic Steps:**
1. **Backup current gulpfile.js**
   ```bash
   cp gulpfile.js gulpfile.js.gulp3.backup
   ```

2. **Update Gulp and plugins:**
   ```bash
   npm install --save-dev gulp@^5.0.0
   npm install --save-dev gulp-sass@^6.0.0
   # Update other gulp-* plugins as needed
   ```

3. **Update gulpfile.js for Gulp 5 API:**
   - Change task definitions from `gulp.task('name', function() {})` to `function name() {}`
   - Export tasks: `exports.taskName = taskName;`
   - Use `gulp.series()` for sequential tasks
   - Use `gulp.parallel()` for parallel tasks
   - Update default task to use series/parallel

4. **Example migration pattern:**
   ```js
   // Gulp 3 (OLD)
   gulp.task('sass', function() {
     return gulp.src('./sass/**/*.scss')
       .pipe(sass())
       .pipe(gulp.dest('./static'));
   });

   gulp.task('default', ['sass', 'watch']);

   // Gulp 5 (NEW)
   function compileSass() {
     return gulp.src('./sass/**/*.scss')
       .pipe(sass())
       .pipe(gulp.dest('./static'));
   }

   function watchFiles() {
     gulp.watch('./sass/**/*.scss', compileSass);
   }

   exports.sass = compileSass;
   exports.watch = watchFiles;
   exports.default = gulp.series(compileSass, watchFiles);
   ```

5. **Test each Gulp task individually:**
   ```bash
   gulp sass
   gulp watch  # Test and manually verify
   gulp build  # If defined
   ```

6. **Update Makefile if it calls Gulp:**
   ```makefile
   build-semantic:
       npx gulp build
   ```

7. **Update any CI/CD scripts using Gulp**

8. **Document Gulp 5 task usage in README or docs/**

**Success Criteria:**
- [ ] Gulp updated to 5.0.1
- [ ] All Gulp tasks functional
- [ ] `gulp` runs default task successfully
- [ ] `gulp sass` compiles Sass correctly
- [ ] `gulp watch` watches and rebuilds
- [ ] Semantic UI build process works
- [ ] No deprecation warnings
- [ ] Makefile targets still work

**Validation:**
```bash
npx gulp --version  # Should show "CLI version: X.X.X, Local version: 5.0.1"
npx gulp sass
npx gulp build
make build-semantic
# Verify outputs match expected
```

**Testing Checklist:**
- [ ] Individual tasks run successfully
- [ ] Series tasks execute in order
- [ ] Parallel tasks execute concurrently
- [ ] Watch mode detects changes
- [ ] Errors are handled gracefully
- [ ] Semantic UI builds correctly

**Risk Assessment:**
- **High Risk:** Breaking changes in Gulp API
- **Mitigation:** Keep backup, test incrementally, rollback plan ready
- **Common Issues:**
  - Task dependencies now require explicit series/parallel
  - Some plugins may need updates for Gulp 5
  - Stream handling differences

**Rollback Plan:**
```bash
git checkout -- gulpfile.js
npm install --save-dev gulp@^3.9.1
npm install
```

---

## Task 1.6: Template Bug Fixes & Validation

**Objective:** Complete pagination fixes and add comprehensive template validation

**Size:** Small (2 hours)
**Priority:** HIGH
**Context Boundary:** 3 files

**Prerequisites:**
- Current template structure understood
- Recent pagination fixes reviewed

**Files Required:**
1. `layouts/partials/meta.html` (primary)
2. `layouts/_default/list.html` (supporting)
3. `layouts/section/photography.html` (supporting)

**Atomic Steps:**
1. **Review recent pagination fixes:**
   - Read commits: 3212737, 8f35aa5, 2173b93, 639fef9, 408798f
   - Document what was fixed and what remains

2. **Audit all template usage of pagination:**
   ```bash
   grep -r "\.Paginator" layouts/
   grep -r "\.IsPaginated" layouts/
   ```

3. **Fix layouts/partials/meta.html:**
   - Ensure proper nil checks before accessing .Paginator
   - Verify .IsNode check before .IsPaginated
   - Add defensive guards for all page types

4. **Add validation for all page types:**
   - Homepage (index.html)
   - List pages (_default/list.html)
   - Single pages (_default/single.html)
   - Photography section (section/photography.html)
   - Photography singles (photography/single.html)
   - 404 page

5. **Create error boundary template:**
   ```
   layouts/partials/safe-paginator.html
   ```
   - Safely check if pagination exists
   - Return empty string if not applicable

6. **Test all page types with Hugo:**
   ```bash
   cd /home/tstapler/Programming/personal-website
   hugo --themesDir=themes --theme=espouse
   # Check for template errors
   ```

7. **Document template requirements:**
   - Which templates support pagination
   - Required front matter fields
   - Safe usage patterns

**Success Criteria:**
- [ ] Zero template execution errors
- [ ] All page types render correctly
- [ ] Pagination works on list pages
- [ ] Non-paginated pages don't error
- [ ] Error boundaries prevent crashes
- [ ] Documentation updated

**Validation:**
```bash
# From parent site directory
hugo --themesDir=themes --theme=espouse --verbose
# Should complete with no template errors

# Test specific page types
hugo server --themesDir=themes --theme=espouse
# Manually visit:
# - / (homepage)
# - /articles/ (list page with pagination)
# - /articles/some-post/ (single page)
# - /photography/ (photography section)
# - /does-not-exist/ (404 page)
```

**Testing Checklist:**
- [ ] Homepage renders without errors
- [ ] List pages show pagination if >10 items
- [ ] List pages work without pagination if <10 items
- [ ] Single pages render correctly
- [ ] Photography section renders
- [ ] 404 page works
- [ ] No nil pointer errors in logs

**Code Pattern Example:**
```go-html-template
{{/* Safe pagination check */}}
{{ if and .IsNode (isset .Paginator "NumberOfElements") }}
  {{ if gt .Paginator.NumberOfElements 0 }}
    {{/* Pagination meta tags */}}
  {{ end }}
{{ end }}
```

---

## Task 1.7: Integration Testing & Verification

**Objective:** Verify all Phase 1 updates work together cohesively

**Size:** Micro (1 hour)
**Priority:** HIGH (MUST DO LAST)
**Context Boundary:** All updated files

**Prerequisites:**
- ALL tasks 1.1-1.6 completed
- Clean git state

**Validation Steps:**

1. **Clean Build Test:**
   ```bash
   make clean
   rm -rf node_modules package-lock.json
   npm install
   npm run build
   make build-semantic
   ```

2. **Security Verification:**
   ```bash
   npm audit
   # Expect: 0 critical, 0 high
   ```

3. **Build Output Verification:**
   ```bash
   ls -lh static/js/
   ls -lh static/*.css
   # Compare sizes to baseline
   ```

4. **Template Rendering Test:**
   ```bash
   cd /home/tstapler/Programming/personal-website
   hugo --themesDir=themes --theme=espouse
   # Should build site with no errors
   ```

5. **Browser Testing:**
   ```bash
   hugo server --themesDir=themes --theme=espouse
   # Visit http://localhost:1313
   # Test all page types
   # Check DevTools console for errors
   ```

6. **Performance Baseline:**
   - Run Lighthouse audit on localhost
   - Document scores for comparison
   - Save report to docs/lighthouse/

**Success Criteria:**
- [ ] Clean install and build succeeds
- [ ] Zero npm audit critical/high issues
- [ ] All Gulp tasks work
- [ ] All webpack tasks work
- [ ] Templates render without errors
- [ ] Site works in browser
- [ ] No console errors
- [ ] Performance baseline documented

**Deliverables:**
- [ ] Updated package.json and package-lock.json
- [ ] Updated webpack.config.js (if changed)
- [ ] Updated gulpfile.js
- [ ] Fixed template files
- [ ] Security audit report in docs/
- [ ] Lighthouse baseline in docs/
- [ ] Git commit with detailed message

**Final Verification Checklist:**
```
✓ Security: npm audit shows 0 critical, 0 high
✓ Build: npm run build succeeds
✓ Build: make build-semantic succeeds
✓ Tools: Gulp 5 tasks work
✓ Tools: Dart Sass compiles correctly
✓ Code: Babel transpiles modern JS
✓ Templates: Hugo builds site without errors
✓ Browser: Site loads without console errors
✓ Browser: Interactive features work
✓ Docs: All changes documented
✓ Git: Changes committed with clear message
```

---

## Summary

**Total Estimated Time:** 12-16 hours

**Parallel Opportunities:**
- Tasks 1.2 and 1.3 can run in parallel after 1.1
- Task 1.6 can run in parallel with 1.2 and 1.3

**Critical Path:**
```
1.1 → 1.4 → 1.5 → 1.7
      (2-3h) (3-4h) (1h)
```

**Recommended Execution Order:**
1. Task 1.1 (Security Audit) - FIRST
2. Task 1.2 (jQuery Update) - Quick win
3. Task 1.3 (Babel Update) - Parallel with 1.2
4. Task 1.6 (Template Fixes) - Parallel with 1.2/1.3
5. Task 1.4 (node-sass → sass) - After 1.1
6. Task 1.5 (Gulp Migration) - After 1.4
7. Task 1.7 (Integration Test) - LAST

**Risk Mitigation:**
- Commit after each successful task
- Test builds incrementally
- Keep backups of critical files
- Document any issues encountered

**Next Steps After Phase 1:**
- Proceed to Phase 2: Webpack 5 Migration
- See `docs/tasks/phase2-build-modernization.md` (to be created)
