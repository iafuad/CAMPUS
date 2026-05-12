/* lost_found.js — JS only where strictly necessary */

var selectedTags = new Map();

function renderSelectedTags() {
  var container   = document.getElementById('e-selectedTags');
  var placeholder = document.getElementById('e-tagsPlaceholder');
  var hiddenWrap  = document.getElementById('tag-hidden-inputs');
  if (!container) return;

  container.querySelectorAll('.selected-chip').forEach(function (c) { c.remove(); });
  if (hiddenWrap) hiddenWrap.innerHTML = '';

  if (selectedTags.size === 0) {
    if (placeholder) placeholder.style.display = '';
  } else {
    if (placeholder) placeholder.style.display = 'none';

    selectedTags.forEach(function (name, id) {
      var chip = document.createElement('span');
      chip.className  = 'selected-chip';
      chip.dataset.id = id;
      chip.innerHTML  = name +
        '<button class="chip-remove" type="button" onclick="removeTag(\'' + id + '\')">×</button>';
      container.appendChild(chip);

      if (hiddenWrap) {
        var input   = document.createElement('input');
        input.type  = 'hidden';
        input.name  = 'tags';
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

function filterTags(query) {
  var anyVisible = false;
  document.querySelectorAll('.pool-item').forEach(function (item) {
    if (item.classList.contains('pool-item--selected')) return;
    var matches = !query || fuzzyMatch(query, item.dataset.name);
    item.style.display = matches ? '' : 'none';
    if (matches) anyVisible = true;
  });
  var poolEmpty = document.getElementById('e-tagsPoolEmpty');
  if (poolEmpty) poolEmpty.style.display = anyVisible ? 'none' : '';
}

function syncTagPoolChips() {
  document.querySelectorAll('.pool-item').forEach(function (item) {
    var selected = selectedTags.has(item.dataset.id);
    item.classList.toggle('pool-item--selected', selected);
    if (selected) item.style.display = 'none';
  });
}

function addTag(el) {
  var id = el.dataset.id;
  if (selectedTags.has(id)) return;
  selectedTags.set(id, el.dataset.name);
  el.classList.add('pool-item--selected');
  el.style.display = 'none';
  renderSelectedTags();
  var search = document.getElementById('e-tagSearch');
  filterTags(search ? search.value : '');
}

function removeTag(id) {
  selectedTags.delete(id);
  renderSelectedTags();
  var item = document.querySelector('.pool-item[data-id="' + id + '"]');
  if (item) {
    item.classList.remove('pool-item--selected');
    var q = document.getElementById('e-tagSearch').value;
    item.style.display = (!q || fuzzyMatch(q, item.dataset.name)) ? '' : 'none';
    filterTags(q);
  }
}

document.addEventListener('DOMContentLoaded', function () {

  /* ── 1. Auto-dismiss flash messages after 5 s ─────────────── */
  document.querySelectorAll('.message').forEach(function (el) {
    setTimeout(function () {
      el.style.transition = 'opacity .4s';
      el.style.opacity = '0';
      setTimeout(function () { el.remove(); }, 400);
    }, 5000);
  });

  /* ── 2. Photo upload preview ──────────────────────────────── */
  var photoInput = document.getElementById('id_uploaded_photos');
  if (photoInput) {
    photoInput.addEventListener('change', function () {
      var preview = document.getElementById('photo-preview');
      if (!preview) return;
      preview.innerHTML = '';

      var files = Array.from(this.files);
      files.forEach(function (file) {
        if (!file.type.startsWith('image/')) return;
        var reader = new FileReader();
        reader.onload = function (e) {
          var img = document.createElement('img');
          img.src = e.target.result;
          img.alt = file.name;
          preview.appendChild(img);
        };
        reader.readAsDataURL(file);
      });
    });
  }

  /* ── 3. Tag picker for lost & found posts ──────────────── */
  document.querySelectorAll('#e-selectedTags .selected-chip').forEach(function (chip) {
    var nameEl = chip.firstChild;
    var name   = nameEl ? nameEl.textContent.trim() : chip.dataset.id;
    selectedTags.set(chip.dataset.id, name);
  });

  syncTagPoolChips();

  var tagSearch = document.getElementById('e-tagSearch');
  if (tagSearch) {
    tagSearch.addEventListener('input', function () {
      filterTags(this.value);
    });
  }

});