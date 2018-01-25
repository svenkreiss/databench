/**
 * Test documentation.
 */

import * as child_process from 'child_process';
import { expect } from 'chai';
import * as Databench from '.';


describe('Server Process', () => {
  let databench_process_return_code = -42;
  const databench_process = child_process.spawn('databench', [
    '--log', 'WARNING',
    '--analyses', 'databench.tests.analyses',
    '--coverage', '.coverage',
    '--some-test-flag',
  ]);
  databench_process.stdout.on('data', data => console.log('databench stdout: ' + data));
  databench_process.stderr.on('data', data => console.log('databench stderr: ' + data));
  databench_process.on('exit', code => {
    databench_process_return_code = code;
    console.log('databench process exited with code ' + code);
  });

  before(done => {
    setTimeout(() => {
      expect(databench_process_return_code).to.equal(-42);
      done();
    }, 1000);
  });

  after(() => databench_process.kill());

  describe('Echo Tests', () => {
    let c = new Databench.Connection();
    beforeEach(() => { c.disconnect(); c = Databench.connect('ws://localhost:5000/parameters/ws'); });
    after(() => c.disconnect());

    it('creates a WebSocket connection', () => {
      expect(typeof c).to.equal('object');
    });

    it('sends an action without message', (done) => {
      c.on('test_action_ack', () => done());
      c.emit('test_action');
    });

    it('echos an object', done => {
      c.on('test_fn', data => {
        expect(data).to.deep.equal([1, 2]);
        done();
      });
      c.emit('test_fn', [1, 2]);
    });

    it('echos an empty string', done => {
      c.on('test_fn', dataEmpty => {
        expect(dataEmpty).to.deep.equal(['', 100]);
        done();
      });
      c.emit('test_fn', '');
    });

    it('echos a null parameter', done => {
      c.on('test_fn', dataNull => {
        expect(dataNull).to.deep.equal([null, 100]);
        done();
      });
      c.emit('test_fn', null);
    });
  });

  describe('Command Line and Request Arguments', () => {
    describe('empty request args', () => {
      const c = new Databench.Connection('ws://localhost:5000/requestargs/ws');
      after(() => c.disconnect());

      it('valid empty request args', done => {
        c.on('echo_request_args', request_args => {
          expect(request_args).to.deep.equal({});
          done();
        });
        c.connect();
      });
    });

    describe('simple request args', () => {
      const c = new Databench.Connection('ws://localhost:5000/requestargs/ws', '?data=requestargtest');
      after(() => c.disconnect());

      it('can access request args', done => {
        c.on('echo_request_args', request_args => {
          expect(request_args).to.deep.equal({ data: ['requestargtest'] });
          done();
        });
        c.connect();
      });
    });

    describe('simple cli args', () => {
      const c = new Databench.Connection('ws://localhost:5000/cliargs/ws');
      after(() => c.disconnect());

      it('can access cli args', done => {
        c.on({ data: 'cli_args' }, args => {
          expect(args).to.deep.equal(['--some-test-flag']);
          done();
        });
        c.connect();
      });
    });
  });

  describe('Cycle Connection', () => {
    let c = new Databench.Connection();
    before(() => { c = Databench.connect('ws://localhost:5000/requestargs/ws'); });
    after(() => c.disconnect());

    it('reconnects after disconnect', done => {
      c.disconnect();
      c.on('echo_request_args', () => done());
      c.connect();
    });
  });

  describe('Analysis Test', () => {
    let c: Databench.Connection = new Databench.Connection();
    beforeEach(() => { c.disconnect(); c = new Databench.Connection(); });
    after(() => c.disconnect());

    it('can open a connection without connecting', done => {
      c.preEmit('test', message => done());
      c.emit('test');
    });

    it('can emulate an empty backend response', done => {
      c.on('received', message => done());
      c.preEmit('test', message => c.trigger('received'));
      c.emit('test');
    });

    it('can emulate a string backend response', () => {
      c.on('received', message => {
        expect(message).to.equal('test message');
      });
      c.preEmit('test', message => c.trigger('received', 'test message'));
      c.emit('test');
    });
  });

  ['parameters', 'parameters_py'].forEach(analysis => {
    describe(`Parameter Tests for ${analysis}`, () => {
      let databench = new Databench.Connection();
      beforeEach(() => { databench.disconnect(); databench = Databench.connect(`ws://localhost:5000/${analysis}/ws`); });
      after(() => databench.disconnect());

      it('calls an action without parameter', done => {
        databench.on('test_action_ack', () => done());
        databench.emit('test_action');
      });

      it('calls an action with an empty string', done => {
        databench.on('test_fn', data => {
          expect(data).to.deep.equal(['', 100]);
          done();
        });
        databench.emit('test_fn', '');
      });

      it('calls an action with a single int', done => {
        databench.on('test_fn', data => {
          expect(data).to.deep.equal([1, 100]);
          done();
        });
        databench.emit('test_fn', 1);
      });

      it('calls an action with a list', done => {
        databench.on('test_fn', data => {
          expect(data).to.deep.equal([1, 2]);
          done();
        });
        databench.emit('test_fn', [1, 2]);
      });

      it('calls an action with a dictionary', done => {
        databench.on('test_fn', data => {
          expect(data).to.deep.equal([1, 2]);
          done();
        });
        databench.emit('test_fn', {first_param: 1, second_param: 2});
      });

      it('calls an action that sets data', done => {
        databench.on({data: 'light'}, data => {
          expect(data).to.equal('red');
          done();
        });
        databench.emit('test_data', ['light', 'red']);
      });

      it('calls an action that sets state', done => {
        databench.on({data: 'light'}, data => {
          expect(data).to.equal('red');
          done();
        });
        databench.emit('test_set_data', ['light', 'red']);
      });

      it('calls an action that sets class data', done => {
        databench.on({class_data: 'light'}, data => {
          expect(data).to.equal('red');
          done();
        });
        databench.emit('test_class_data', ['light', 'red']);
      });

      it('calls an action that well emit process states', done => {
        databench.on('test_fn', data => expect(data).to.deep.equal([1, 100]));
        databench.onProcess(123, data => {
          expect(data).to.be.oneOf(['start', 'end']);
          if (data == 'end') done();
        });
        databench.emit('test_fn', {first_param: 1, __process_id: 123});
      });
    });
  });

});
