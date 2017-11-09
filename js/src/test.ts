/**
 * Test documentation.
 *
 * Bla.
 */

import { expect } from 'chai';
import * as Databench from '.';


describe('Echo Tests', () => {
  it('creates a WebSocket connection', () => {
    const c = Databench.connect('ws://localhost:5000/parameters/ws');
    expect(typeof c).to.equal('object');
  });

  it('sends an action without message', (done) => {
    const c = Databench.connect('ws://localhost:5000/parameters/ws');
    c.on('test_action_ack', () => done());
    c.emit('test_action');
  });

  it('echos an object', done => {
    const c = Databench.connect('ws://localhost:5000/parameters/ws');
    c.on('test_fn', data => {
      expect(data).to.deep.equal([1, 2]);
      done();
    });
    c.emit('test_fn', [1, 2]);
  });

  it('echos an empty string', done => {
    const c = Databench.connect('ws://localhost:5000/parameters/ws');
    c.on('test_fn', dataEmpty => {
      expect(dataEmpty).to.deep.equal(['', 100]);
      done();
    });
    c.emit('test_fn', '');
  });

  it('echos a null parameter', done => {
    const c = Databench.connect('ws://localhost:5000/parameters/ws');
    c.on('test_fn', dataNull => {
      expect(dataNull).to.deep.equal([null, 100]);
      done();
    });
    c.emit('test_fn', null);
  });
});

describe('Command Line and Request Arguments', () => {
  it('valid empty request args', done => {
    const c = new Databench.Connection('ws://localhost:5000/requestargs/ws');
    c.on('echo_request_args', request_args => {
      expect(request_args).to.deep.equal({});
      done();
    });
    c.connect();
  });

  it('can access request args', done => {
    const c = new Databench.Connection('ws://localhost:5000/requestargs/ws', '?data=requestargtest');
    c.on('echo_request_args', request_args => {
      expect(request_args).to.deep.equal({ data: ['requestargtest'] });
      done();
    });
    c.connect();
  });

  it('can access cli args', done => {
    const c = new Databench.Connection('ws://localhost:5000/cliargs/ws');
    c.on({ data: 'cli_args' }, args => {
      expect(args).to.deep.equal(['--some-test-flag']);
      done();
    });
    c.connect();
  });
});

describe('Cycle Connection', () => {
  it('reconnects after disconnect', done => {
    // create connection
    const c = Databench.connect('ws://localhost:5000/requestargs/ws');
    c.disconnect();
    c.on('echo_request_args', () => done());
    c.connect();
  });
});

describe('Analysis Test', () => {
  it('can open a connection without connecting', done => {
    const c = new Databench.Connection();
    c.preEmit('test', message => done());
    c.emit('test');
  });

  it('can emulate an empty backend response', done => {
    const c = new Databench.Connection();
    c.on('received', message => done());
    c.preEmit('test', message => c.trigger('received'));
    c.emit('test');
  });

  it('can emulate a string backend response', () => {
    const c = new Databench.Connection();
    c.on('received', message => {
      expect(message).to.equal('test message');
    });
    c.preEmit('test', message => c.trigger('received', 'test message'));
    c.emit('test');
  });
});
