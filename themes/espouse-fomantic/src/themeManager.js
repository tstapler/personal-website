/**
 * Theme Manager
 * Handles dark/light mode switching with localStorage persistence
 * and system preference detection
 */

class ThemeManager {
  constructor() {
    this.storageKey = 'theme-preference';
    this.themes = {
      LIGHT: 'light',
      DARK: 'dark'
    };

    // Initialize theme on load
    this.init();
  }

  /**
   * Initialize theme based on saved preference or system preference
   */
  init() {
    const savedTheme = this.getSavedTheme();
    const systemPreference = this.getSystemPreference();

    // Priority: saved preference > system preference > light (default)
    const theme = savedTheme || systemPreference || this.themes.LIGHT;

    this.applyTheme(theme);
    this.setupToggleListeners();
    this.setupSystemPreferenceListener();
  }

  /**
   * Get saved theme from localStorage
   * @returns {string|null} Saved theme or null
   */
  getSavedTheme() {
    try {
      return localStorage.getItem(this.storageKey);
    } catch (e) {
      console.warn('localStorage not available:', e);
      return null;
    }
  }

  /**
   * Save theme preference to localStorage
   * @param {string} theme - Theme to save
   */
  saveTheme(theme) {
    try {
      localStorage.setItem(this.storageKey, theme);
    } catch (e) {
      console.warn('Could not save theme preference:', e);
    }
  }

  /**
   * Get system color scheme preference
   * @returns {string|null} System preference or null
   */
  getSystemPreference() {
    if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
      return this.themes.DARK;
    }
    if (window.matchMedia && window.matchMedia('(prefers-color-scheme: light)').matches) {
      return this.themes.LIGHT;
    }
    return null;
  }

  /**
   * Apply theme to document
   * @param {string} theme - Theme to apply
   */
  applyTheme(theme) {
    const validTheme = theme === this.themes.DARK ? this.themes.DARK : this.themes.LIGHT;
    document.documentElement.setAttribute('data-theme', validTheme);

    // Update meta theme-color for mobile browsers
    this.updateMetaThemeColor(validTheme);
  }

  /**
   * Update meta theme-color tag
   * @param {string} theme - Current theme
   */
  updateMetaThemeColor(theme) {
    let metaThemeColor = document.querySelector('meta[name="theme-color"]');

    if (!metaThemeColor) {
      metaThemeColor = document.createElement('meta');
      metaThemeColor.name = 'theme-color';
      document.head.appendChild(metaThemeColor);
    }

    metaThemeColor.content = theme === this.themes.DARK ? '#1a1a1a' : '#ffffff';
  }

  /**
   * Toggle between light and dark themes
   */
  toggleTheme() {
    const currentTheme = document.documentElement.getAttribute('data-theme');
    const newTheme = currentTheme === this.themes.DARK ? this.themes.LIGHT : this.themes.DARK;

    this.applyTheme(newTheme);
    this.saveTheme(newTheme);

    // Dispatch custom event for other components to react
    window.dispatchEvent(new CustomEvent('themechange', {
      detail: { theme: newTheme }
    }));
  }

  /**
   * Get current theme
   * @returns {string} Current theme
   */
  getCurrentTheme() {
    return document.documentElement.getAttribute('data-theme') || this.themes.LIGHT;
  }

  /**
   * Setup click listeners for theme toggle buttons
   */
  setupToggleListeners() {
    const toggleButtons = document.querySelectorAll('.theme-toggle');

    toggleButtons.forEach(button => {
      button.addEventListener('click', () => this.toggleTheme());

      // Keyboard accessibility
      button.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' || e.key === ' ') {
          e.preventDefault();
          this.toggleTheme();
        }
      });
    });
  }

  /**
   * Listen for system preference changes
   */
  setupSystemPreferenceListener() {
    if (!window.matchMedia) return;

    const darkModeQuery = window.matchMedia('(prefers-color-scheme: dark)');

    // Modern browsers
    if (darkModeQuery.addEventListener) {
      darkModeQuery.addEventListener('change', (e) => {
        // Only update if user hasn't set explicit preference
        if (!this.getSavedTheme()) {
          const newTheme = e.matches ? this.themes.DARK : this.themes.LIGHT;
          this.applyTheme(newTheme);
        }
      });
    }
    // Legacy browsers
    else if (darkModeQuery.addListener) {
      darkModeQuery.addListener((e) => {
        if (!this.getSavedTheme()) {
          const newTheme = e.matches ? this.themes.DARK : this.themes.LIGHT;
          this.applyTheme(newTheme);
        }
      });
    }
  }
}

// Initialize theme manager when DOM is ready
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', () => {
    window.themeManager = new ThemeManager();
  });
} else {
  window.themeManager = new ThemeManager();
}

// Export for module systems
if (typeof module !== 'undefined' && module.exports) {
  module.exports = ThemeManager;
}
