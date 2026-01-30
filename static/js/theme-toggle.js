/**
 * Theme Toggle - Dark/Light Mode Management
 * Stores preference in localStorage and applies to HTML element
 */

class ThemeToggle {
    constructor() {
        this.htmlElement = document.documentElement;
        this.toggleButton = document.getElementById('themeToggle');
        this.storageKey = 'banking-app-theme';
        this.darkTheme = 'dark';
        this.lightTheme = 'light';
        
        this.init();
    }

    init() {
        // Load saved preference or use system preference
        this.loadTheme();
        
        // Add event listener to toggle button
        if (this.toggleButton) {
            this.toggleButton.addEventListener('click', () => this.toggle());
        }

        // Listen for system theme changes
        if (window.matchMedia) {
            window.matchMedia('(prefers-color-scheme: dark)')
                .addListener(() => this.loadTheme());
        }
    }

    /**
     * Load theme from localStorage or system preference
     */
    loadTheme() {
        const savedTheme = localStorage.getItem(this.storageKey);
        
        if (savedTheme) {
            this.setTheme(savedTheme);
        } else {
            // Check system preference
            const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
            this.setTheme(prefersDark ? this.darkTheme : this.lightTheme);
        }
    }

    /**
     * Set theme and update UI
     */
    setTheme(theme) {
        // Validate theme
        if (theme !== this.darkTheme && theme !== this.lightTheme) {
            theme = this.lightTheme;
        }

        // Apply to HTML element (Bootstrap 5.3)
        this.htmlElement.setAttribute('data-bs-theme', theme);

        // Update localStorage
        localStorage.setItem(this.storageKey, theme);

        // Update button icon
        this.updateButtonIcon(theme);

        // Dispatch custom event for other components
        window.dispatchEvent(new CustomEvent('themechange', { detail: { theme } }));
    }

    /**
     * Update toggle button icon
     */
    updateButtonIcon(theme) {
        if (!this.toggleButton) return;

        const icon = this.toggleButton.querySelector('i');
        if (!icon) return;

        if (theme === this.darkTheme) {
            icon.classList.remove('fa-moon');
            icon.classList.add('fa-sun');
            this.toggleButton.title = 'Switch to light mode';
        } else {
            icon.classList.remove('fa-sun');
            icon.classList.add('fa-moon');
            this.toggleButton.title = 'Switch to dark mode';
        }
    }

    /**
     * Toggle between light and dark mode
     */
    toggle() {
        const currentTheme = this.htmlElement.getAttribute('data-bs-theme') || this.lightTheme;
        const newTheme = currentTheme === this.lightTheme ? this.darkTheme : this.lightTheme;
        this.setTheme(newTheme);
    }

    /**
     * Get current theme
     */
    getCurrentTheme() {
        return this.htmlElement.getAttribute('data-bs-theme') || this.lightTheme;
    }

    /**
     * Check if dark mode is enabled
     */
    isDarkMode() {
        return this.getCurrentTheme() === this.darkTheme;
    }
}

// Initialize on DOM ready
document.addEventListener('DOMContentLoaded', () => {
    window.themeToggle = new ThemeToggle();
});

// Fallback initialization
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        if (!window.themeToggle) {
            window.themeToggle = new ThemeToggle();
        }
    });
} else {
    if (!window.themeToggle) {
        window.themeToggle = new ThemeToggle();
    }
}
