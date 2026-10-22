
document.querySelectorAll('input[data-filter]').forEach(function(inp){
  inp.addEventListener('input', function(){
    var q = inp.value.toLowerCase();
    var table = document.querySelector(inp.dataset.filter);
    if(!table) return;
    table.querySelectorAll('tbody tr').forEach(function(tr){
      tr.style.display = tr.innerText.toLowerCase().indexOf(q) > -1 ? '' : 'none';
    });
  });
});
