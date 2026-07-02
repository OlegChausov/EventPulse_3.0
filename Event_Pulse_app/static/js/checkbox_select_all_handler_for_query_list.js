const form = document.getElementById('querylist-form');
const selectAll = form.querySelector('#select-all-queries');
const getRowChecks = () => Array.from(form.querySelectorAll('.row-check'));

selectAll.addEventListener('change', () => {
  getRowChecks().forEach(cb => cb.checked = selectAll.checked);
});

form.addEventListener('change', (e) => {
  if (!e.target.classList.contains('row-check')) return;
  const checks = getRowChecks();
  selectAll.checked = checks.length && checks.every(c => c.checked);
});
