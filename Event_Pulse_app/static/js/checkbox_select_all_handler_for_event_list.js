(function() {
  const form = document.getElementById('events-form');
  const selectAll = form.querySelector('#select-all');
  const getRowChecks = () => Array.from(form.querySelectorAll('.row-check'));
  selectAll.addEventListener('change', () => {
    getRowChecks().forEach(cb => cb.checked = selectAll.checked);
  });
  form.addEventListener('change', (e) => {
    if (!e.target.classList.contains('row-check')) return;
    const checks = getRowChecks();
    selectAll.checked = checks.length && checks.every(c => c.checked);
  });
})();