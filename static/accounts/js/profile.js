/* profile.js — Edit-page only.
   Responsibilities:
     1. Skill chip picker — add/remove selected skills as chips and
        keep hidden <input> elements in sync so the form POST carries them.
     2. Photo upload preview — show a thumbnail before submitting.
   The edit form submits as a standard multipart POST and the view redirects.
*/

/* ── Skill chip picker ─────────────────────────────────────── */

/* Tracks id → name for currently selected skills */
var selectedSkills = new Map();

function renderSelectedChips() {
  var container   = document.getElementById('e-selectedChips');
  var placeholder = document.getElementById('e-chipsPlaceholder');
  var hiddenWrap  = document.getElementById('skill-hidden-inputs');
  if (!container) return;

  /* Remove existing chips and hidden inputs — we'll re-render both */
  container.querySelectorAll('.selected-chip').forEach(function (c) { c.remove(); });
  if (hiddenWrap) hiddenWrap.innerHTML = '';

  if (selectedSkills.size === 0) {
    if (placeholder) placeholder.style.display = '';
  } else {
    if (placeholder) placeholder.style.display = 'none';

    selectedSkills.forEach(function (name, id) {
      /* Visible chip */
      var chip = document.createElement('span');
      chip.className  = 'selected-chip';
      chip.dataset.id = id;
      chip.innerHTML  = name +
        '<button class="chip-remove" type="button" onclick="removeSkill(\'' + id + '\')">×</button>';
      container.appendChild(chip);

      /* Hidden input so the regular form POST sends this skill id */
      if (hiddenWrap) {
        var input   = document.createElement('input');
        input.type  = 'hidden';
        input.name  = 'skill_ids';
        input.value = id;
        hiddenWrap.appendChild(input);
      }
    });
  }
}

function fuzzyMatch(query, str) {
  var q  = query.toLowerCase();
  var s  = str.toLowerCase();
  var qi = 0;
  for (var i = 0; i < s.length && qi < q.length; i++) {
    if (s[i] === q[qi]) qi++;
  }
  return qi === q.length;
}

function filterSkills(query) {
  var anyVisible = false;
  document.querySelectorAll('.pool-item').forEach(function (item) {
    if (item.classList.contains('pool-item--selected')) return;
    var matches = !query || fuzzyMatch(query, item.dataset.name);
    item.style.display = matches ? '' : 'none';
    if (matches) anyVisible = true;
  });
  var poolEmpty = document.getElementById('e-poolEmpty');
  if (poolEmpty) poolEmpty.style.display = anyVisible ? 'none' : '';
}

function syncPoolChips() {
  document.querySelectorAll('.pool-item').forEach(function (item) {
    var selected = selectedSkills.has(item.dataset.id);
    item.classList.toggle('pool-item--selected', selected);
    if (selected) item.style.display = 'none';
  });
}

function addSkill(el) {
  var id = el.dataset.id;
  if (selectedSkills.has(id)) return;
  selectedSkills.set(id, el.dataset.name);
  el.classList.add('pool-item--selected');
  el.style.display = 'none';
  renderSelectedChips();
  var search = document.getElementById('e-skillSearch');
  filterSkills(search ? search.value : '');
}

function removeSkill(id) {
  selectedSkills.delete(id);
  renderSelectedChips();
  var item = document.querySelector('.pool-item[data-id="' + id + '"]');
  if (item) {
    item.classList.remove('pool-item--selected');
    var q = document.getElementById('e-skillSearch').value;
    item.style.display = (!q || fuzzyMatch(q, item.dataset.name)) ? '' : 'none';
    filterSkills(q);
  }
}

/* ── Photo upload preview ──────────────────────────────────── */

function previewPhoto(input) {
  var file = input.files[0];
  if (!file) return;

  var img      = document.getElementById('e-photoPreviewImg');
  var initials = document.getElementById('e-photoInitials');
  var filename = document.getElementById('e-photoFilename');

  if (img) {
    img.src          = URL.createObjectURL(file);
    img.style.display = '';
  }
  if (initials) initials.style.display = 'none';
  if (filename) filename.textContent   = file.name;
}

/* ── Initialise on DOM ready ───────────────────────────────── */

document.addEventListener('DOMContentLoaded', function () {
  /* Pre-populate selectedSkills from chips already rendered by the template
     (current user's skills passed from the view). */
  document.querySelectorAll('#e-selectedChips .selected-chip').forEach(function (chip) {
    var nameEl = chip.firstChild; /* text node before the remove button */
    var name   = nameEl ? nameEl.textContent.trim() : chip.dataset.id;
    selectedSkills.set(chip.dataset.id, name);
  });

  /* Hide already-selected items in the pool */
  syncPoolChips();

  /* Wire up search input */
  var search = document.getElementById('e-skillSearch');
  if (search) {
    search.addEventListener('input', function () {
      filterSkills(this.value);
    });
  }
});