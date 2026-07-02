document.addEventListener('DOMContentLoaded', function() {
  M.FormSelect.init(document.querySelectorAll('select'));
});

document.body.addEventListener('htmx:afterSwap', function(evt) {
  var elems = evt.target.querySelectorAll('select');
  if (elems.length) {
    M.FormSelect.init(elems);
  }
});