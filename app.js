// BASE BEHAVIOUR. Mechanics only — no component wiring.
//
// The old app.js drove a specific mobile menu, a specific lightbox, a specific gallery
// filter and a specific sun/moon toggle. Each assumed particular markup, so every derived
// site inherited the same interactions and the same silhouette. Gone.
//
// What is left is the theme MECHANISM (persist a choice, otherwise follow the OS) and a
// reduced-motion helper. Both are face-neutral. Wire your own controls to them.

(() => {
  'use strict';

  const KEY = 'theme';
  const root = document.documentElement;

  const osDark = () => matchMedia('(prefers-color-scheme: dark)').matches;
  const stored = () => { try { return localStorage.getItem(KEY); } catch { return null; } };

  // An explicit choice if one was made, otherwise whatever the OS says.
  const current = () => root.getAttribute('data-theme') || (osDark() ? 'dark' : 'light');

  function setTheme(next) {
    root.setAttribute('data-theme', next);
    try { localStorage.setItem(KEY, next); } catch { /* private mode: this page only */ }
    root.dispatchEvent(new CustomEvent('themechange', { detail: { theme: next } }));
  }

  // Keep following the OS until the visitor makes an explicit choice.
  matchMedia('(prefers-color-scheme: dark)').addEventListener('change', () => {
    if (!stored()) root.removeAttribute('data-theme');
  });

  // Public surface. Build whatever control you like:
  //   <button data-theme-toggle aria-pressed="false">…</button>  is wired automatically
  //   site.setTheme('dark') / site.toggleTheme() / site.theme() / site.prefersReducedMotion()
  window.site = {
    setTheme,
    theme: current,
    toggleTheme: () => setTheme(current() === 'dark' ? 'light' : 'dark'),
    prefersReducedMotion: () => matchMedia('(prefers-reduced-motion: reduce)').matches,
  };

  document.addEventListener('click', (e) => {
    const btn = e.target.closest('[data-theme-toggle]');
    if (!btn) return;
    window.site.toggleTheme();
    btn.setAttribute('aria-pressed', String(current() === 'dark'));
  });
})();
