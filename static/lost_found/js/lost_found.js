/* lost_found.js — JS only where strictly necessary */

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

});