import { expect } from 'chai';
import * as Databench from './../src';


describe('Databench', () => {
  describe('Connection', () => {
    // create connection
    const c = new Databench.Connection(
      null,
      'ws://localhost:5000/parameters/ws'
    ).connect();

    it('create a WebSocket connection', () => {
      expect(typeof c).to.equal('object');
    });

    it('action without message', (done) => {
      c.on('test_action_ack', () => { done(); });
      c.emit('test_action');
    });

    it('echo an object', done => {
      c.on('test_fn', data => {
        expect(data).to.deep.equal([1, 2]);
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
        expect(dataEmpty).to.deep.equal(['', 100]);
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
        expect(dataNull).to.deep.equal([null, 100]);
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
      expect(typeof c).to.equal('object');
    });

    it('request args test', done => {
      c.on('ack', () => done());
      c.connect();
    });
  });

  describe('Cli Args', () => {
    // create connection
    const c = new Databench.Connection(
      null,
      'ws://localhost:5000/cliargs/ws'
    );

    it('create a WebSocket connection', () => {
      expect(typeof c).to.equal('object');
    });

    it('command args test', done => {
      c.on({ data: 'cli_args' }, (args) => {
        expect(args).to.deep.equal(['--some-test-flag']);
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
      expect(typeof c).to.equal('object');
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
