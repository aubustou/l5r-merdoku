(function () {
  'use strict';

  function closeModal() {
    const c = document.getElementById('modal-container');
    if (c) c.innerHTML = '';
  }

  // Esc closes modal
  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape') closeModal();
  });

  // Tab switching in modal
  window.merdokuTab = function (btn) {
    const card = btn.closest('.modal-card');
    if (!card) return;
    card.querySelectorAll('.tab-btn').forEach(function (b) {
      b.classList.toggle('active', b === btn);
    });
    const tab = btn.dataset.tab;
    card.querySelectorAll('.tab-panel').forEach(function (p) {
      p.hidden = p.dataset.panel !== tab;
    });
  };

  window.merdokuCloseModal = closeModal;
})();
