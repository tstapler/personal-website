// Vanilla-JS site enhancements. Loaded after the prebuilt Fomantic bundles, so it must not
// depend on jQuery. Ported from espouse/src/semanticExtras.js (kept dependency-free so no
// webpack rebuild is needed).
(function () {
  'use strict'

  // Menu button: keyboard activation, and aria-expanded derived from the sidebar's real state
  // (the dimmer can close the sidebar without going through the button).
  function initMenuButton() {
    var btn = document.getElementById('menuButton')
    var sidebar = document.querySelector('.ui.sidebar')
    if (!btn) return
    btn.setAttribute('role', 'button')
    btn.setAttribute('tabindex', '0')
    btn.setAttribute('aria-label', 'Open navigation menu')
    btn.setAttribute('aria-expanded', 'false')
    btn.addEventListener('keydown', function (e) {
      if (e.key !== 'Enter' && e.key !== ' ') return
      e.preventDefault()
      btn.click()
    })
    if (!sidebar) return
    new MutationObserver(function () {
      btn.setAttribute('aria-expanded', String(sidebar.classList.contains('visible')))
    }).observe(sidebar, { attributes: true, attributeFilter: ['class'] })
  }

  function flashCopied(btn) {
    btn.textContent = '✓ Copied'
    btn.classList.add('copied')
    setTimeout(function () { btn.textContent = 'Copy'; btn.classList.remove('copied') }, 2000)
  }

  function fallbackCopy(text, btn) {
    var ta = document.createElement('textarea')
    ta.value = text
    ta.style.cssText = 'position:fixed;opacity:0'
    document.body.appendChild(ta)
    ta.select()
    document.execCommand('copy')
    document.body.removeChild(ta)
    flashCopied(btn)
  }

  function addCopyButtons() {
    document.querySelectorAll('article pre:not(.mermaid)').forEach(function (pre) {
      var btn = document.createElement('button')
      btn.className = 'copy-btn'
      btn.textContent = 'Copy'
      btn.setAttribute('aria-label', 'Copy code to clipboard')
      btn.addEventListener('click', function () {
        var text = (pre.querySelector('code') || pre).innerText
        if (!navigator.clipboard) return fallbackCopy(text, btn)
        navigator.clipboard.writeText(text).then(function () { flashCopied(btn) }, function () { fallbackCopy(text, btn) })
      })
      pre.appendChild(btn)
    })
  }

  function addHeadingAnchors() {
    var article = document.querySelector('#content')
    if (!article) return
    article.querySelectorAll('h2[id], h3[id]').forEach(function (h) {
      var a = document.createElement('a')
      a.className = 'heading-anchor'
      a.href = '#' + h.id
      a.setAttribute('aria-label', 'Link to this section')
      a.textContent = '#'
      h.appendChild(a)
    })
  }

  function initReadingProgress() {
    var bar = document.getElementById('reading-progress')
    if (!bar) return
    function update() {
      var scrolled = window.scrollY || window.pageYOffset
      var total = document.documentElement.scrollHeight - window.innerHeight
      bar.style.transform = 'scaleX(' + (total > 0 ? scrolled / total : 0) + ')'
    }
    window.addEventListener('scroll', update, { passive: true })
    update()
  }

  function initTOCHighlight() {
    var toc = document.getElementById('TableOfContents')
    if (!toc) return
    var headings = Array.from(document.querySelectorAll('#content h2[id], #content h3[id]'))
    if (!headings.length) return
    var links = {}
    headings.forEach(function (h) {
      var a = toc.querySelector('a[href="#' + h.id + '"]')
      if (a) links[h.id] = a
    })
    function update() {
      var current = headings[0]
      headings.forEach(function (h) { if (h.getBoundingClientRect().top < 120) current = h })
      Object.keys(links).forEach(function (id) { links[id].classList.remove('toc-active') })
      if (links[current.id]) links[current.id].classList.add('toc-active')
    }
    window.addEventListener('scroll', update, { passive: true })
    update()
  }

  // Native <dialog> lightbox. The prebuilt Fomantic modal never finishes its close transition
  // (CSS/JS version skew), so it is pre-empted here: the capture-phase listener runs before the
  // bundle's handler on the figure and stops the event. Images wrapped in links keep their link.
  function initLightbox() {
    if (typeof HTMLDialogElement === 'undefined') return
    document.addEventListener('click', function (e) {
      var img = e.target.closest && e.target.closest('.post-image img')
      if (!img || img.closest('a[href]')) return
      e.stopPropagation()
      var dialog = document.createElement('dialog')
      dialog.className = 'lightbox'
      var big = document.createElement('img')
      big.src = img.currentSrc || img.src
      big.alt = img.alt
      dialog.appendChild(big)
      dialog.addEventListener('click', function () { dialog.close() })
      dialog.addEventListener('close', function () { dialog.remove() })
      document.body.appendChild(dialog)
      dialog.showModal()
    }, true)
  }

  function init() {
    initLightbox()
    initMenuButton()
    addCopyButtons()
    addHeadingAnchors()
    initReadingProgress()
    initTOCHighlight()
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init)
  else init()
})()
