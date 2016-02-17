var assert = require('assert');
var Databench = require('./../node_client/main');

describe('Databench', function() {
  describe('#Connection', function () {
    // create connection
    var c = new Databench.Connection(
      function(msg) { console.log(msg) },
      null,
      'http://localhost:5000/dummypi/ws'
    );

    it('create a WebSocket connection', function () {
      assert.equal('object', typeof c);
    });

    it('echo an object', function (done) {
      this.timeout(5000);

      var d;
      c.on('test_fn', function(data) { d = data; });
      c.emit('test_fn', [1, 2]);

      setTimeout(function() {
        assert.deepEqual({first_param: 1, second_param: 2}, d);
        done();
      }, 100);
    });
  });
});
