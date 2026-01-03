const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

async function validateSummaryFix() {
  console.log('🔍 Validating summary overflow fix...');
  
  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage();
  
  try {
    // Start local Hugo server
    console.log('📡 Starting Hugo server...');
    const { spawn } = require('child_process');
    const hugoProcess = spawn('hugo', ['server', '-D', '-p', '1313'], {
      stdio: 'pipe'
    });
    
    // Wait for server to start
    await new Promise(resolve => setTimeout(resolve, 5000));
    
    // Navigate to test page
    await page.goto('http://localhost:1313/test-summaries/', {
      waitUntil: 'networkidle'
    });
    
    const results = {
      timestamp: new Date().toISOString(),
      tests: [],
      summary: {},
      screenshots: []
    };

    // Test 1: Card Height Consistency
    console.log('📏 Testing card height consistency...');
    const cards = await page.$$('.ui.card');
    const heights = [];
    
    for (const card of cards) {
      const height = await page.evaluate((el) => 
        el.getBoundingClientRect().height, card
      );
      heights.push(height);
    }
    
    const maxHeight = Math.max(...heights);
    const minHeight = Math.min(...heights);
    const heightVariance = maxHeight - minHeight;
    
    results.tests.push({
      name: 'Card Height Consistency',
      passed: heightVariance < 10, // Allow 10px tolerance
      details: {
        heights,
        variance: heightVariance,
        maxHeight,
        minHeight
      }
    });

    // Test 2: Overflow Detection
    console.log('🌊 Testing for overflow...');
    let overflowCount = 0;
    for (const card of cards) {
      const summary = await card.$('.card-summary-content');
      if (summary) {
        const hasOverflow = await page.evaluate((el) => {
          return el.scrollHeight > el.clientHeight || el.scrollWidth > el.clientWidth;
        }, summary);
        
        if (hasOverflow) overflowCount++;
      }
    }
    
    results.tests.push({
      name: 'Overflow Detection',
      passed: overflowCount === 0,
      details: {
        overflowCount,
        totalCards: cards.length
      }
    });

    // Test 3: Read More Links
    console.log('🔗 Testing Read More links...');
    const longSummaryCards = await page.$$('.ui.card');
    let readMoreCount = 0;
    
    for (const card of longSummaryCards) {
      const readMore = await card.$('a[href*="test-summaries"]');
      if (readMore) readMoreCount++;
    }
    
    results.tests.push({
      name: 'Read More Links',
      passed: readMoreCount >= 1,
      details: {
        readMoreCount,
        totalCards: longSummaryCards.length
      }
    });

    // Test 4: CSS Class Application
    console.log('🎨 Testing CSS class application...');
    const summaryElements = await page.$$('.card-summary-content');
    let classesApplied = 0;
    
    for (const element of summaryElements) {
      const hasClass = await page.evaluate((el) => 
        el.classList.contains('card-summary-content'), element
      );
      if (hasClass) classesApplied++;
    }
    
    results.tests.push({
      name: 'CSS Class Application',
      passed: classesApplied === summaryElements.length,
      details: {
        elementsWithClass: classesApplied,
        totalSummaryElements: summaryElements.length
      }
    });

    // Take screenshots for visual verification
    console.log('📸 Taking screenshots...');
    await page.screenshot({ 
      path: path.join(__dirname, '..', 'test-results/summary-cards-full.png'), 
      fullPage: true 
    });
    
    // Close-up of card heights
    await page.evaluate(() => {
      const cards = document.querySelectorAll('.ui.card');
      cards.forEach((card, index) => {
        card.style.border = '2px solid red';
        card.style.position = 'relative';
      });
    });
    
    await page.screenshot({ 
      path: path.join(__dirname, '..', 'test-results/summary-cards-with-borders.png'), 
      fullPage: true 
    });

    // Summary
    const allPassed = results.tests.every(test => test.passed);
    results.summary = {
      allTestsPassed: allPassed,
      totalTests: results.tests.length,
      passedTests: results.tests.filter(test => test.passed).length,
      failedTests: results.tests.filter(test => !test.passed).length
    };

    // Save results
    const outputPath = path.join(__dirname, '..', 'test-results', 'validation-results.json');
    fs.writeFileSync(outputPath, JSON.stringify(results, null, 2));
    
    // Kill Hugo process
    hugoProcess.kill();
    
    console.log(`\\n✅ Validation complete: ${results.summary.passedTests}/${results.summary.totalTests} tests passed`);
    
    // Print detailed results
    results.tests.forEach(test => {
      const status = test.passed ? '✅' : '❌';
      console.log(`  ${status} ${test.name}`);
      if (!test.passed) {
        console.log(`    Details: ${JSON.stringify(test.details, null, 2)}`);
      }
    });
    
    await browser.close();
    return results;
    
  } catch (error) {
    console.error('❌ Validation failed:', error);
    await browser.close();
    throw error;
  }
}

if (require.main === module) {
  validateSummaryFix()
    .then(() => process.exit(0))
    .catch(error => {
      console.error(error);
      process.exit(1);
    });
}

module.exports = { validateSummaryFix };