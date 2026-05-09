// ── Helpers ────────────────────────────────────────────────────────
function getCsrfToken() {
  return document.cookie
    .split('; ')
    .find((row) => row.startsWith('csrftoken='))
    ?.split('=')[1];
}

// Notification helpers
function toggleNotif() {
  const dropdown = document.getElementById('notifDropdown');
  if (!dropdown) return;
  dropdown.classList.toggle('open');
}

function clearNotifs() {
  const notifications = document.getElementById('notifList');
  if (!notifications) return;
  notifications.innerHTML = '<div class="notif-empty">No notifications.</div>';
}

// ── Skills state: Map<id (string) → name> ─────────────────────────
let selectedSkills = new Map();

function renderSelectedChips() {
  const container = document.getElementById('e-selectedChips');
  const placeholder = document.getElementById('e-chipsPlaceholder');
  if (!container || !placeholder) return;

  container.querySelectorAll('.selected-chip').forEach((c) => c.remove());

  if (selectedSkills.size === 0) {
    placeholder.style.display = '';
  } else {
    placeholder.style.display = 'none';
    selectedSkills.forEach((name, id) => {
      const chip = document.createElement('span');
      chip.className = 'selected-chip';
      chip.dataset.id = id;
      chip.innerHTML =
        name +
        `<button class="chip-remove" type="button" onclick="removeSkill('${id}')">×</button>`;
      container.appendChild(chip);
    });
  }
}

function fuzzyMatch(query, str) {
  const q = query.toLowerCase();
  const s = str.toLowerCase();
  let qi = 0;
  for (let i = 0; i < s.length && qi < q.length; i++) {
    if (s[i] === q[qi]) qi++;
  }
  return qi === q.length;
}

function filterSkills(query) {
  let anyVisible = false;
  document.querySelectorAll('.pool-item').forEach((item) => {
    if (item.classList.contains('pool-item--selected')) return;
    const matches = !query || fuzzyMatch(query, item.dataset.name);
    item.style.display = matches ? '' : 'none';
    if (matches) anyVisible = true;
  });
  const poolEmpty = document.getElementById('e-poolEmpty');
  if (poolEmpty) {
    poolEmpty.style.display = anyVisible ? 'none' : '';
  }
}

function syncPoolChips() {
  document.querySelectorAll('.pool-item').forEach((item) => {
    const selected = selectedSkills.has(item.dataset.id);
    item.classList.toggle('pool-item--selected', selected);
    if (selected) item.style.display = 'none';
  });
}

function addSkill(el) {
  const id = el.dataset.id;
  if (selectedSkills.has(id)) return;
  selectedSkills.set(id, el.dataset.name);
  el.classList.add('pool-item--selected');
  el.style.display = 'none';
  renderSelectedChips();
  filterSkills(document.getElementById('e-skillSearch').value);
}

function removeSkill(id) {
  selectedSkills.delete(id);
  renderSelectedChips();
  const item = document.querySelector(`.pool-item[data-id="${id}"]`);
  if (item) {
    item.classList.remove('pool-item--selected');
    const q = document.getElementById('e-skillSearch').value;
    item.style.display = (!q || fuzzyMatch(q, item.dataset.name)) ? '' : 'none';
    filterSkills(q);
  }
}

function openEditModal() {
  const firstName = document.getElementById('v-firstName');
  const lastName = document.getElementById('v-lastName');
  const studentId = document.getElementById('v-studentId');
  const bio = document.getElementById('v-bio');

  document.getElementById('e-firstName').value = firstName
    ? firstName.textContent.trim().replace('—', '')
    : '';
  document.getElementById('e-lastName').value = lastName
    ? lastName.textContent.trim().replace('—', '')
    : '';
  document.getElementById('e-studentId').value = studentId
    ? studentId.textContent.trim().replace('Not set', '')
    : '';
  document.getElementById('e-bio').value = bio
    ? bio.textContent.trim().replace('No bio added yet.', '')
    : '';

  selectedSkills = new Map();
  document.querySelectorAll('#v-skills .skill-tag[data-id]').forEach((tag) => {
    selectedSkills.set(tag.dataset.id, tag.textContent.trim());
  });

  renderSelectedChips();
  syncPoolChips();

  const search = document.getElementById('e-skillSearch');
  if (search) search.value = '';
  filterSkills('');

  const errorBox = document.getElementById('editError');
  if (errorBox) errorBox.style.display = 'none';

  const modal = document.getElementById('editModal');
  if (modal) {
    modal.style.display = 'flex';
    document.body.style.overflow = 'hidden';
  }
}

function closeEditModal() {
  const modal = document.getElementById('editModal');
  if (modal) {
    modal.style.display = 'none';
    document.body.style.overflow = '';
  }
}

async function saveProfile() {
  const saveBtn = document.getElementById('saveBtn');
  const errorBox = document.getElementById('editError');

  const payload = {
    first_name: document.getElementById('e-firstName').value.trim(),
    last_name: document.getElementById('e-lastName').value.trim(),
    student_id: document.getElementById('e-studentId').value.trim(),
    department_id: document.getElementById('e-dept').value || null,
    bio: document.getElementById('e-bio').value.trim(),
    skill_ids: Array.from(selectedSkills.keys()).map((id) => parseInt(id)),
  };

  if (saveBtn) {
    saveBtn.disabled = true;
    saveBtn.textContent = 'Saving…';
  }
  if (errorBox) {
    errorBox.style.display = 'none';
  }

  try {
    const url = document.getElementById('editUrl').dataset.url;
    const res = await fetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': getCsrfToken(),
      },
      body: JSON.stringify(payload),
    });

    const data = await res.json();
    if (!res.ok || data.error) {
      if (errorBox) {
        errorBox.textContent = data.error || 'Something went wrong.';
        errorBox.style.display = 'block';
      }
      return;
    }

    document.getElementById('displayName').textContent =
      data.first_name + ' ' + data.last_name;
    document.getElementById('v-firstName').textContent = data.first_name || '—';
    document.getElementById('v-lastName').textContent = data.last_name || '—';
    document.getElementById('v-studentId').textContent = data.student_id || 'Not set';
    document.getElementById('v-dept').textContent = data.department_name || 'Not set';
    document.getElementById('v-bio').textContent = data.bio || 'No bio added yet.';

    const skillsWrap = document.getElementById('v-skills');
    if (skillsWrap) {
      if (data.skills && data.skills.length > 0) {
        skillsWrap.innerHTML = '';
        data.skills.forEach((skill) => {
          const span = document.createElement('span');
          span.className = 'skill-tag';
          span.dataset.id = skill.id;
          span.textContent = skill.name;
          skillsWrap.appendChild(span);
        });
      } else {
        skillsWrap.innerHTML =
          '<span class="skill-tag empty-msg">No skills added yet.</span>';
      }
    }

    closeEditModal();
    if (typeof showToast === 'function') {
      showToast('✅ Profile saved!');
    }
  } catch (err) {
    if (errorBox) {
      errorBox.textContent = 'Network error — please try again.';
      errorBox.style.display = 'block';
    }
  } finally {
    if (saveBtn) {
      saveBtn.disabled = false;
      saveBtn.textContent = 'Save Profile →';
    }
  }
}
