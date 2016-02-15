'use strict';

var assert = require('assert');
var Databench = require('./../node/main');

describe('Databench', function() {
  describe('#Connection', function () {
    it('create a WebSocket connection', function () {
      let c = new Databench.Connection(
        (msg) => console.log(msg),
        null,
        'http://localhost:5000/dummypi/ws'
      );
      assert.equal('object', typeof c);
    });
  });
});
