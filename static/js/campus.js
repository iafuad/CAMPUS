/* campus.js — Dark mode toggle
   The actual theme *application* (reading localStorage) runs inline in
   <head> via a tiny script tag to prevent flash-of-unstyled-content.
   This file only wires up the toggle button after the DOM is ready.
*/

document.addEventListener('DOMContentLoaded', function () {
  var btn = document.getElementById('theme-toggle');
  if (!btn) return;

  btn.addEventListener('click', function () {
    var current = document.documentElement.getAttribute('data-theme');
    var next    = current === 'dark' ? 'light' : 'dark';

    document.documentElement.setAttribute('data-theme', next);
    localStorage.setItem('campus-theme', next);

    // Update aria-label for accessibility
    btn.setAttribute(
      'aria-label',
      next === 'dark' ? 'Switch to light mode' : 'Switch to dark mode'
    );
  });
});