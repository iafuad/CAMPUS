(function () {
  const grid = document.querySelector('.post-grid');
  if (!grid) return;

  const state = { type: 'all', category: 'all', status: 'all', sort: 'newest' };

  // Deduplicate category options
  const catSelect = document.querySelector('[data-filter="category"]');
  const seen = new Set();
  [...catSelect.options].forEach(opt => {
    if (opt.value === 'all') { seen.add('all'); return; }
    if (seen.has(opt.value)) opt.remove();
    else seen.add(opt.value);
  });

  function applyFilters() {
    const cards = [...grid.querySelectorAll('.post-card')];
    let visible = 0;

    cards.forEach(card => {
      const matchType     = state.type     === 'all' || card.dataset.type     === state.type;
      const matchCategory = state.category === 'all' || card.dataset.category === state.category;
      const matchStatus   = state.status   === 'all' || card.dataset.status   === state.status;
      const show = matchType && matchCategory && matchStatus;
      card.style.display = show ? '' : 'none';
      if (show) visible++;
    });

    // Sort visible cards by date (stored in the date meta-item text)
    const visibleCards = cards.filter(c => c.style.display !== 'none');
    visibleCards.sort((a, b) => {
      const da = new Date(a.querySelector('.post-card__meta-item:last-child').textContent.trim());
      const db = new Date(b.querySelector('.post-card__meta-item:last-child').textContent.trim());
      return state.sort === 'newest' ? db - da : da - db;
    });
    visibleCards.forEach(c => grid.appendChild(c));

    const count = document.getElementById('filterCount');
    count.textContent = visible === cards.length ? '' : `${visible} of ${cards.length}`;
  }

  // Pills
  document.querySelectorAll('.lf-filter-pill').forEach(btn => {
    btn.addEventListener('click', () => {
      document.querySelectorAll(`.lf-filter-pill[data-filter="${btn.dataset.filter}"]`)
        .forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      state[btn.dataset.filter] = btn.dataset.value;
      applyFilters();
    });
  });

  // Selects
  document.querySelectorAll('.lf-filter-select').forEach(sel => {
    sel.addEventListener('change', () => {
      state[sel.dataset.filter] = sel.value;
      applyFilters();
    });
  });
})();