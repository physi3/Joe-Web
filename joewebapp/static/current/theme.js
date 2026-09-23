const THEME_KEY = 'theme';
const VALID_THEMES = ['dark', 'light'];

function switchTheme(theme) {
  const safeTheme = VALID_THEMES.includes(theme) ? theme : 'dark';

  if (document.body) {
    document.body.setAttribute('data-theme', safeTheme);
  }

  if (document.documentElement) {
    document.documentElement.setAttribute('data-theme', safeTheme);
  }

  try {
    localStorage.setItem(THEME_KEY, safeTheme);
  } catch (error) {
    console.warn('Theme could not be saved:', error);
  }
}

function initializeTheme() {
  const defaultTheme = document.body ? document.body.dataset.defaultTheme || 'dark' : 'dark';

  try {
    const savedTheme = localStorage.getItem(THEME_KEY);
    switchTheme(savedTheme && VALID_THEMES.includes(savedTheme) ? savedTheme : defaultTheme);
  } catch (error) {
    switchTheme(defaultTheme);
  }
}

if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', initializeTheme, { once: true });
} else {
  initializeTheme();
}
