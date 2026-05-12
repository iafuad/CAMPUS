// apps/forum/static/forum/js/forum.js

document.addEventListener('DOMContentLoaded', () => {
  const fuzzyInput = document.getElementById('fuzzy-search-input');
  const suggestionsBox = document.getElementById('search-suggestions-box');
  
  let debounceTimer;

  if (fuzzyInput) {
    fuzzyInput.addEventListener('input', () => {
      clearTimeout(debounceTimer);
      const query = fuzzyInput.value.trim();
      if (query.length < 2) { suggestionsBox.style.display = 'none'; return; }

      debounceTimer = setTimeout(async () => {
        const response = await fetch(`/forum/search-suggestions/?q=${encodeURIComponent(query)}`);
        const data = await response.json();
        renderSuggestions(data);
      }, 250);
    });
  }

  function renderSuggestions(data) {
    suggestionsBox.innerHTML = '';
    let hasResults = false;

    const sections = [
      { title: 'Departments', items: data.departments, type: 'dept' },
      { title: 'Courses', items: data.courses, type: 'course' }
    ];

    sections.forEach(section => {
      if (section.items.length > 0) {
        hasResults = true;
        const head = document.createElement('div');
        head.className = 'suggestion-header';
        head.textContent = section.title;
        suggestionsBox.appendChild(head);

        section.items.forEach(item => {
          const div = document.createElement('div');
          div.className = 'suggestion-item';
          div.textContent = item.label;
          div.onclick = () => applyFilter(section.type, item);
          suggestionsBox.appendChild(div);
        });
      }
    });
    suggestionsBox.style.display = hasResults ? 'block' : 'none';
  }

  function applyFilter(type, item) {
    const params = new URLSearchParams(window.location.search);
    if (type === 'dept') {
      params.set('department', item.id);
    } else {
      params.set('course', item.code);
    }
    window.location.search = params.toString();
  }

  // Close when clicking outside
  document.addEventListener('click', (e) => {
    if (fuzzyInput && !fuzzyInput.contains(e.target)) suggestionsBox.style.display = 'none';
  });
});