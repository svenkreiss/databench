/* global describe it */
const assert = require('assert');
const Databench = require('./../build/node_client/main');


describe('Databench', () => {
  describe('Connection', () => {
    // create connection
    const c = new Databench.Connection(
      null,
      'ws://localhost:5000/parameters/ws'
    ).connect();

    it('create a WebSocket connection', () => {
      assert.equal('object', typeof c);
    });

    it('action without message', (done) => {
      c.on('test_action_ack', () => { done(); });
      c.emit('test_action');
    });

    it('echo an object', done => {
      c.on('test_fn', data => {
        assert.deepEqual([1, 2], data);
        done();
      });
      c.emit('test_fn', [1, 2]);
    });
  });


  describe('Connection for empty string', () => {
    // create connection
    const c = new Databench.Connection(
      null,
      'ws://localhost:5000/parameters/ws'
    ).connect();

    it('echo an empty string', done => {
      c.on('test_fn', dataEmpty => {
        assert.deepEqual(['', 100], dataEmpty);
        done();
      });
      c.emit('test_fn', '');
    });
  });

  describe('Connection for null', () => {
    // create connection
    const c = new Databench.Connection(
      null,
      'ws://localhost:5000/parameters/ws'
    ).connect();

    it('echo a null parameter', done => {
      c.on('test_fn', dataNull => {
        assert.deepEqual([null, 100], dataNull);
        done();
      });
      c.emit('test_fn', null);
    });
  });

  describe('Request Args', () => {
    // create connection
    const c = new Databench.Connection(
      null,
      'ws://localhost:5000/requestargs/ws',
      '?data=requestargtest'
    );

    it('create a WebSocket connection', () => {
      assert.equal('object', typeof c);
    });

    it('request args test', done => {
      c.on('ack', () => done());
      c.connect();
    });
  });

  describe('Cmd Args', () => {
    // create connection
    const c = new Databench.Connection(
      null,
      'ws://localhost:5000/cmdargs/ws'
    );

    it('create a WebSocket connection', () => {
      assert.equal('object', typeof c);
    });

    it('command args test', done => {
      c.on({ data: 'cmd_args' }, (args) => {
        assert.deepEqual(['--some-test-flag'], args);
        done();
      });
      c.connect();
    });
  });

  describe('disconnect', () => {
    // create connection
    const c = new Databench.Connection(
      null,
      'ws://localhost:5000/requestargs/ws',
      '?data=requestargtest'
    );

    it('create a WebSocket connection', () => {
      assert.equal('object', typeof c);
    });

    it('connect', () => {
      c.connect();
    });

    it('disconnect', () => {
      c.disconnect();
    });

    it('reconnect', done => {
      c.on('ack', () => done());
      c.connect();
    });
  });
});
