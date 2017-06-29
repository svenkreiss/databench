import { expect } from 'chai';
import * as Databench from '.';


describe('Databench', () => {
  describe('Echo Tests', () => {
    it('create a WebSocket connection', () => {
      const c = Databench.connect('ws://localhost:5000/parameters/ws');
      expect(typeof c).to.equal('object');
    });

    it('action without message', (done) => {
      const c = Databench.connect('ws://localhost:5000/parameters/ws');
      c.on('test_action_ack', () => done());
      c.emit('test_action');
    });

    it('echo an object', done => {
      const c = Databench.connect('ws://localhost:5000/parameters/ws');
      c.on('test_fn', data => {
        expect(data).to.deep.equal([1, 2]);
        done();
      });
      c.emit('test_fn', [1, 2]);
    });

    it('echo an empty string', done => {
      const c = Databench.connect('ws://localhost:5000/parameters/ws');
      c.on('test_fn', dataEmpty => {
        expect(dataEmpty).to.deep.equal(['', 100]);
        done();
      });
      c.emit('test_fn', '');
    });

    it('echo a null parameter', done => {
      const c = Databench.connect('ws://localhost:5000/parameters/ws');
      c.on('test_fn', dataNull => {
        expect(dataNull).to.deep.equal([null, 100]);
        done();
      });
      c.emit('test_fn', null);
    });
  });

  describe('Command line and Request Arguments', () => {
    it('request args test', done => {
      const c = new Databench.Connection('ws://localhost:5000/requestargs/ws', '?data=requestargtest');
      c.on('echo_request_args', (request_args: string) => {
        expect(request_args).to.deep.equal({ data: ['requestargtest'] });
        done();
      });
      c.connect();
    });

    it('cli args test', done => {
      const c = new Databench.Connection('ws://localhost:5000/cliargs/ws');
      c.on({ data: 'cli_args' }, (args) => {
        expect(args).to.deep.equal(['--some-test-flag']);
        done();
      });
      c.connect();
    });
  });

  describe('Cycle Connection', () => {
    it('reconnect', done => {
      // create connection
      const c = Databench.connect('ws://localhost:5000/requestargs/ws');
      c.disconnect();
      c.on('echo_request_args', () => done());
      c.connect();
    });
  });
});
