# Phase 2: Build System Modernization - Atomic Task Breakdown

## Overview

**Phase Goal:** Modernize webpack to v5, optimize performance, and reduce bundle sizes
**Total Estimated Effort:** 20-24 hours
**Priority:** HIGH
**Context Boundary:** 2-5 files per task, 2-4 hours per task

## Task Dependency Graph

```
┌─────────────────────────────────┐
│ Task 2.1: Webpack 5 Migration   │ (6-8h) - START HERE
└──────────────┬──────────────────┘
               │
               ▼
┌─────────────────────────────────┐
│ Task 2.2: Update Webpack Plugins│ (4-6h) - DEPENDS ON 2.1
└──────────────┬──────────────────┘
               │
               ├──────────────────────┐
               ▼                      ▼
┌──────────────────────┐  ┌─────────────────────────────┐
│ Task 2.3: Performance│  │ Task 2.4: CSS Modernization │
│ Optimization (4-6h)  │  │ (3-4h)                      │
└──────────────────────┘  └─────────────────────────────┘
               │                      │
               └──────────┬───────────┘
                          ▼
               ┌─────────────────────────────┐
               │ Task 2.5: Bundle Analysis   │ (2-3h)
               │ & Final Optimization        │
               └─────────────────────────────┘
```

## Task 2.1: Webpack 5 Migration

**Objective:** Update webpack from v4 to v5 with breaking changes handled

**Size:** Large (6-8 hours)
**Priority:** CRITICAL
**Context Boundary:** 3 files

**Prerequisites:**
- Phase 1 complete (Dart Sass working)
- Current webpack 4 build functional

**Files Required:**
1. `webpack.config.js` (primary - major changes)
2. `package.json` (dependency updates)
3. `package-lock.json` (supporting)

**Breaking Changes to Address:**

1. **Automatic Node.js Polyfills Removed**
   - Webpack 5 no longer includes polyfills for Node.js core modules
   - May need to add fallbacks for crypto, stream, etc.

2. **Persistent Caching**
   - New feature requiring configuration
   - Significantly improves rebuild performance

3. **Asset Modules**
   - Replaces file-loader, url-loader, raw-loader
   - Need to migrate to asset/resource, asset/inline

4. **Optimization Defaults Changed**
   - Better defaults, but some manual config may need updating

5. **Plugin API Changes**
   - Some plugins need webpack 5 compatible versions

**Atomic Steps:**

1. **Backup current configuration:**
   ```bash
   cp webpack.config.js webpack.config.js.webpack4.backup
   cp package.json package.json.webpack4.backup
   ```

2. **Update webpack core packages:**
   ```bash
   npm install --save-dev webpack@^5.95.0 webpack-cli@^5.1.4
   ```

3. **Check for deprecation warnings:**
   ```bash
   npm run build 2>&1 | grep -i "deprecat"
   ```

4. **Update webpack.config.js for v5:**

   **Remove deprecated plugins:**
   ```js
   // REMOVE this line (no longer needed in webpack 5)
   new webpack.optimize.OccurrenceOrderPlugin(),
   ```

   **Add persistent caching:**
   ```js
   module.exports = {
     cache: {
       type: 'filesystem',
       buildDependencies: {
         config: [__filename],
       },
     },
     // ... rest of config
   };
   ```

   **Migrate loaders to asset modules:**
   ```js
   // OLD (webpack 4)
   {
     test: /\.woff(2)?(\?v=[0-9]\.[0-9]\.[0-9])?$/,
     use: [{
       loader: 'url-loader?limit=10000&mimetype=application/fontwoff&name=[name].[ext]',
     }]
   }

   // NEW (webpack 5)
   {
     test: /\.woff2?$/,
     type: 'asset',
     parser: {
       dataUrlCondition: {
         maxSize: 10000
       }
     }
   }
   ```

   **Update file-loader usages:**
   ```js
   // OLD
   {
     test: /\.(jpe?g|gif|png|ttf|eot|svg)$/,
     use: [{
       loader: 'file-loader?name=[name].[ext]?[hash]',
     }]
   }

   // NEW
   {
     test: /\.(jpe?g|gif|png|ttf|eot|svg)$/,
     type: 'asset/resource',
     generator: {
       filename: '[name][ext]?[hash]'
     }
   }
   ```

5. **Test build:**
   ```bash
   npm run build
   ```

6. **Handle any errors:**
   - Missing polyfills: Add resolve.fallback
   - Plugin compatibility: Check plugin versions
   - Loader issues: Verify asset module migration

**Success Criteria:**
- [ ] Webpack updated to 5.x
- [ ] webpack-cli updated to 5.x
- [ ] Build completes successfully
- [ ] All assets generated correctly
- [ ] Persistent caching configured
- [ ] No deprecation warnings

**Validation:**
```bash
npx webpack --version
npm run build
ls -lh static/js/ static/*.css
# Verify file sizes and integrity
```

**Known Issues & Mitigations:**
- **Issue:** Missing Node.js polyfills
  - **Fix:** Add resolve.fallback configuration
- **Issue:** Plugin incompatibility
  - **Fix:** Update plugins (Task 2.2)
- **Issue:** Asset module configuration
  - **Fix:** Follow migration guide carefully

**Rollback Plan:**
```bash
cp webpack.config.js.webpack4.backup webpack.config.js
cp package.json.webpack4.backup package.json
npm install
```

---

## Task 2.2: Update Webpack Plugins for v5

**Objective:** Update all webpack plugins to webpack 5 compatible versions

**Size:** Medium-Large (4-6 hours)
**Priority:** HIGH (DEPENDS ON Task 2.1)
**Context Boundary:** 4 files

**Prerequisites:**
- Task 2.1 complete (webpack 5 installed)

**Files Required:**
1. `package.json` (primary)
2. `webpack.config.js` (plugin configurations)
3. `package-lock.json` (supporting)
4. Build test outputs

**Plugins to Update:**

| Plugin | Current | Target | Notes |
|--------|---------|--------|-------|
| mini-css-extract-plugin | 0.10.0 | 2.9.4 | Major update |
| css-minimizer-webpack-plugin | 1.1.2 | 7.0.2 | Replace optimize-css-assets |
| terser-webpack-plugin | Auto | 5.x | Better minification |
| babel-minify-webpack-plugin | 0.3.1 | Remove? | Consider terser only |
| compression-webpack-plugin | 4.0.1 | 11.1.0 | Optional upgrade |

**Atomic Steps:**

1. **Update mini-css-extract-plugin:**
   ```bash
   npm install --save-dev mini-css-extract-plugin@^2.9.4
   ```

   **Config changes:**
   ```js
   // No breaking changes, but verify options
   new MiniCssExtractPlugin({
     filename: '[name].css',
     chunkFilename: '[name].[id].css',
   }),
   ```

2. **Replace optimize-css-assets with css-minimizer:**
   ```bash
   npm uninstall optimize-css-assets-webpack-plugin
   npm install --save-dev css-minimizer-webpack-plugin@^7.0.2
   ```

   **Update webpack.config.js:**
   ```js
   const CssMinimizerPlugin = require('css-minimizer-webpack-plugin');

   // Remove OptimizeCssAssetsPlugin from plugins array

   // Add to optimization.minimizer
   optimization: {
     minimizer: [
       `...`, // extends default minimizers (terser)
       new CssMinimizerPlugin(),
     ],
   }
   ```

3. **Update terser-webpack-plugin:**
   ```bash
   npm install --save-dev terser-webpack-plugin@^5.3.0
   ```

   **Update custom terser config if exists:**
   ```js
   const TerserPlugin = require('terser-webpack-plugin');

   optimization: {
     minimizer: [
       new TerserPlugin({
         terserOptions: {
           compress: {
             drop_console: false,
           },
         },
       }),
       new CssMinimizerPlugin(),
     ],
   }
   ```

4. **Review babel-minify-webpack-plugin:**
   - Webpack 5 + terser may be sufficient
   - Consider removing for simpler config
   - Test bundle sizes with/without

5. **Test each plugin update:**
   ```bash
   npm run build
   # Check outputs after each change
   ls -lh static/
   ```

**Success Criteria:**
- [ ] All plugins updated to webpack 5 compatible versions
- [ ] CSS minimizer working (css-minimizer-webpack-plugin)
- [ ] JS minimization working (terser)
- [ ] Build succeeds with all plugins
- [ ] Bundle sizes same or better
- [ ] No deprecation warnings

**Validation:**
```bash
npm list mini-css-extract-plugin css-minimizer-webpack-plugin terser-webpack-plugin
npm run build
# Compare bundle sizes
du -sh static/
```

**Testing Checklist:**
- [ ] CSS files minified correctly
- [ ] JS files minified correctly
- [ ] Source maps generated (if configured)
- [ ] File naming correct
- [ ] Asset hashing working

---

## Task 2.3: Performance Optimization

**Objective:** Implement lazy loading, code splitting, and bundle optimization

**Size:** Medium-Large (4-6 hours)
**Priority:** MEDIUM (AFTER Task 2.2)
**Context Boundary:** 5 files

**Prerequisites:**
- Task 2.2 complete (webpack 5 plugins working)

**Files Required:**
1. `webpack.config.js` (optimization config)
2. `app.js` (entry point)
3. `src/homePage.js` (particles.js lazy load)
4. `layouts/index.html` (async script loading)
5. `layouts/partials/javascript.html` (script loading)

**Atomic Steps:**

1. **Configure webpack bundle splitting:**
   ```js
   optimization: {
     splitChunks: {
       chunks: 'all',
       cacheGroups: {
         vendor: {
           test: /[\\/]node_modules[\\/]/,
           name: 'vendors',
           priority: 10,
         },
         semantic: {
           test: /[\\/]node_modules[\\/]semantic-ui/,
           name: 'semantic',
           priority: 20,
         },
       },
     },
   }
   ```

2. **Implement lazy loading for particles.js:**

   **Update src/homePage.js:**
   ```js
   // OLD - Always loads
   import pJS from "particles.js"

   // NEW - Lazy load
   async function initParticles() {
     const pJS = await import(/* webpackChunkName: "particles" */ "particles.js");
     // ... particles config
   }

   // Only load on homepage
   if (document.getElementById('particles-js')) {
     initParticles();
   }
   ```

3. **Add webpack bundle analyzer:**
   ```bash
   npm install --save-dev webpack-bundle-analyzer
   ```

   **Add to webpack.config.js:**
   ```js
   const BundleAnalyzerPlugin = require('webpack-bundle-analyzer').BundleAnalyzerPlugin;

   plugins: [
     // Add only in analyze mode
     ...(process.env.ANALYZE ? [new BundleAnalyzerPlugin()] : []),
   ]
   ```

   **Add npm script:**
   ```json
   "scripts": {
     "build": "webpack -p",
     "analyze": "ANALYZE=true webpack -p"
   }
   ```

4. **Optimize Semantic UI imports:**
   - Review which Semantic UI components actually used
   - Consider importing only needed components
   - Reduce semantic bundle size

5. **Configure tree shaking:**
   ```js
   optimization: {
     usedExports: true,
     sideEffects: false,
   }
   ```

**Success Criteria:**
- [ ] particles.js loads only on homepage
- [ ] Vendor bundles split appropriately
- [ ] Bundle analyzer working
- [ ] 30-50% reduction in initial bundle size
- [ ] Tree shaking enabled

**Validation:**
```bash
npm run analyze
# Review bundle composition
# Check homepage vs other pages load different bundles
```

**Performance Metrics:**
- Before: Record bundle sizes
- After: Verify 30-50% reduction target
- Lighthouse: Check performance score

---

## Task 2.4: CSS Pipeline Modernization

**Objective:** Update CSS processing pipeline for modern features

**Size:** Medium (3-4 hours)
**Priority:** MEDIUM (PARALLEL with 2.3)
**Context Boundary:** 3 files

**Prerequisites:**
- Task 2.2 complete (css-minimizer-webpack-plugin working)

**Files Required:**
1. `webpack.config.js` (CSS pipeline config)
2. `package.json` (dependencies)
3. `sass/espouse.scss` (test compilation)

**Atomic Steps:**

1. **Update cssnano:**
   ```bash
   npm install --save-dev cssnano@^7.1.2
   ```

2. **Configure modern PostCSS pipeline:**
   ```bash
   npm install --save-dev postcss@^8.4.0 postcss-loader@^8.1.0
   ```

   **Update webpack config:**
   ```js
   {
     test: /\.scss$/,
     use: [
       MiniCssExtractPlugin.loader,
       'css-loader',
       {
         loader: 'postcss-loader',
         options: {
           postcssOptions: {
             plugins: [
               ['autoprefixer'],
               ['cssnano', { preset: 'default' }],
             ],
           },
         },
       },
       {
         loader: 'sass-loader',
         options: {
           implementation: require('sass'),
         },
       },
     ],
   }
   ```

3. **Create postcss.config.js:**
   ```js
   module.exports = {
     plugins: {
       autoprefixer: {},
       cssnano: {
         preset: ['default', {
           discardComments: { removeAll: true },
         }],
       },
     },
   };
   ```

4. **Test CSS output:**
   ```bash
   npm run build
   # Verify CSS is properly processed and minified
   ```

**Success Criteria:**
- [ ] cssnano updated to 7.x
- [ ] PostCSS pipeline working
- [ ] CSS properly autoprefixed
- [ ] CSS minified correctly
- [ ] Smaller CSS bundles

**Validation:**
```bash
npm run build
ls -lh static/*.css
# Check for autoprefixer vendor prefixes
# Verify minification
```

---

## Task 2.5: Bundle Analysis & Final Optimization

**Objective:** Analyze bundles and apply final optimizations

**Size:** Small-Medium (2-3 hours)
**Priority:** LOW (FINAL)
**Context Boundary:** 2 files

**Prerequisites:**
- Tasks 2.1-2.4 complete

**Files Required:**
1. `webpack.config.js` (final tweaks)
2. Bundle analyzer reports

**Atomic Steps:**

1. **Generate bundle analysis:**
   ```bash
   npm run analyze
   ```

2. **Review analysis:**
   - Identify large dependencies
   - Find duplicate code
   - Spot optimization opportunities

3. **Apply targeted optimizations:**
   - Remove unused dependencies
   - Replace large libraries with smaller alternatives
   - Further optimize code splitting

4. **Configure compression:**
   ```js
   const CompressionPlugin = require('compression-webpack-plugin');

   plugins: [
     new CompressionPlugin({
       algorithm: 'gzip',
       test: /\.(js|css|html|svg)$/,
       threshold: 8192,
       minRatio: 0.8,
     }),
   ]
   ```

5. **Document bundle composition:**
   - Create bundle size report
   - Compare before/after metrics
   - Document optimization wins

**Success Criteria:**
- [ ] Bundle analysis complete
- [ ] Target bundle size achieved (30-50% reduction)
- [ ] Compression configured
- [ ] Documentation updated

**Validation:**
```bash
npm run analyze
npm run build
# Compare bundle sizes before/after Phase 2
```

---

## Summary

**Total Estimated Time:** 20-24 hours

**Task Breakdown:**
- Task 2.1: Webpack 5 Migration (6-8h) - CRITICAL PATH
- Task 2.2: Plugin Updates (4-6h) - DEPENDS ON 2.1
- Task 2.3: Performance Optimization (4-6h) - AFTER 2.2
- Task 2.4: CSS Modernization (3-4h) - PARALLEL with 2.3
- Task 2.5: Bundle Analysis (2-3h) - FINAL

**Parallel Opportunities:**
- Tasks 2.3 and 2.4 can run in parallel after 2.2

**Critical Path:**
```
2.1 (6-8h) → 2.2 (4-6h) → 2.3/2.4 (4-6h) → 2.5 (2-3h) = 16-23h
```

**Expected Outcomes:**
- ✅ Webpack 5 with modern features
- ✅ 30-50% bundle size reduction
- ✅ Faster rebuild times (persistent caching)
- ✅ Better performance (lazy loading, code splitting)
- ✅ Modern CSS pipeline
- ✅ Resolved remaining security vulnerabilities

**Next Steps After Phase 2:**
- Phase 3: Feature Enhancements (dark mode, accessibility, PWA)
- See `docs/roadmap.md` for complete plan
