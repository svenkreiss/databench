'use strict';

var assert = require('assert');
var Databench = require('./../node_client/main');

describe('Databench', function() {
  describe('#Connection', function () {
    // create connection
    let c = new Databench.Connection(
      (msg) => console.log(msg),
      null,
      'http://localhost:5000/dummypi/ws'
    );

    it('create a WebSocket connection', function () {
      assert.equal('object', typeof c);
    });

    it('echo an object', function (done) {
      this.timeout(5000);

      let d;
      c.on('test_fn', (data) => { d = data; });
      c.emit('test_fn', [1, 2]);

      setTimeout(() => {
        assert.deepEqual({first_param: 1, second_param: 2}, d);
        done();
      }, 100);
    });
  });
});
