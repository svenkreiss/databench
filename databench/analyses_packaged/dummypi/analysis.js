var d = new Databench.Connection();
Databench.ui.wire(d);

d.on({data: 'pi'}, function(pi) {
  document.getElementById('pi').innerHTML = pi.estimate.toFixed(3)+' ± '+pi.uncertainty.toFixed(3);
});

d.connect();
