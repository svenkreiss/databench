var assert = require('assert');
var Databench = require('./../node_client/main');

describe('Databench', function() {
  describe('Connection', function () {
    // create connection
    var c = new Databench.Connection(
      null,
      'ws://localhost:5000/parameters/ws'
    ).connect();

    it('create a WebSocket connection', function () {
      assert.equal('object', typeof c);
    });

    it('echo an object', function (done) {
      this.timeout(5000);

      var d;
      c.on('test_fn', function(data) { d = data; });
      c.emit('test_fn', [1, 2]);

      setTimeout(function() {
        assert.deepEqual([1, 2], d);
        done();
      }, 100);
    });

    it('action without message', function(done) {
      this.timeout(5000);

      var ack = false;
      c.on('test_action_ack', function() { ack = true; });
      c.emit('test_action');

      setTimeout(function() {
        assert.equal(ack, true);
        done();
      }, 100);
    });
  });
});
