/* threads.js — JS only where strictly necessary:
   1. Auto-scroll message list to latest message on load
   2. Photo preview with per-image remove buttons
   3. File count badge next to attach label
*/

document.addEventListener('DOMContentLoaded', function () {

  /* ── 1. Scroll message list to bottom ─────────────────────── */
  var messageList = document.querySelector('.threads-message-list');
  if (messageList) {
    messageList.scrollTop = messageList.scrollHeight;
  }

  /* ── 2. Photo preview + removable thumbnails ──────────────── */
  var fileInput   = document.getElementById('thread-photos');
  var preview     = document.getElementById('thread-photo-preview');
  var countBadge  = document.getElementById('thread-attach-count');

  if (!fileInput || !preview) return;

  // DataTransfer lets us maintain a mutable file list
  // (file inputs are read-only by spec)
  var dt = new DataTransfer();

  fileInput.addEventListener('change', function () {
    Array.from(this.files).forEach(function (file) {
      if (!file.type.startsWith('image/')) return;
      dt.items.add(file);
    });

    // Sync the real input to our mutable list
    fileInput.files = dt.files;
    renderPreviews();
  });

  function renderPreviews() {
    preview.innerHTML = '';

    Array.from(dt.files).forEach(function (file, index) {
      var item = document.createElement('div');
      item.className = 'threads-compose__preview-item';

      var img = document.createElement('img');
      img.alt = file.name;

      var reader = new FileReader();
      reader.onload = function (e) { img.src = e.target.result; };
      reader.readAsDataURL(file);

      var remove = document.createElement('button');
      remove.type = 'button';
      remove.className = 'threads-compose__preview-remove';
      remove.textContent = '×';
      remove.setAttribute('aria-label', 'Remove ' + file.name);

      remove.addEventListener('click', function () {
        dt.items.remove(index);
        fileInput.files = dt.files;
        renderPreviews();
      });

      item.appendChild(img);
      item.appendChild(remove);
      preview.appendChild(item);
    });

    if (countBadge) {
      countBadge.textContent = dt.files.length > 0
        ? dt.files.length + ' photo' + (dt.files.length > 1 ? 's' : '')
        : '';
    }
  }

});