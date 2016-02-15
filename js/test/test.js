var assert = require('assert');
var Databench = require('./../node/main');

describe('Databench', function() {
  describe('#Connection', function () {
    it('create a WebSocket connection', function () {
      assert.equal('function', typeof Databench.Connection);
    });
  });
});
