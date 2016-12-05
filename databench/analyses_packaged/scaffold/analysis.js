// initialize Databench's frontend library
var d = new Databench.Connection();
Databench.ui.wire(d);

// listen for updates to 'status' in 'data'
d.on({data: 'status'}, function(status) {
  console.log(`received ${JSON.stringify(status)}`);
  document.getElementById('status').innerHTML = status;

  // send 'ack' action back:
  d.emit('ack', 'thanks for sending ready');
});

d.connect();
