from .meta import Meta


class AnalysisTest(object):
    """Unit test wrapper for an analysis.

    :param databench.Analysis analysis: The analysis to test.
    :param str cli_args: Command line interface arguments.
    :param str request_args: Request arguments.
    :param meta: An object with a `run_process` attribute.

    Trigger actions using the `~.trigger` method.
    All outgoing messages to the frontend are captured in `emitted_messages`.

    There are two main options for constructing tests: decorating with
    `tornado.testing.gen_test` and yielding `~tornado.concurrent.Future`
    objects (block until
    future is done) or to use :meth:`~tornado.testing.AsyncTestCase.wait` and
    :meth:`~tornado.testing.AsyncTestCase.stop` in callbacks.
    For detailed information on ioloops within the Tornado testing framework,
    please consult `tornado.testing`.

    :ivar list cli_args: command line arguments
    :ivar dict request_args: request arguments
    :ivar list emitted_messages: all emitted (``signal``, ``message``) pairs

    Examples:

    .. literalinclude:: ../databench/tests/test_testing.py
        :language: python
    """
    def __init__(self, analysis, cli_args=None, request_args=None, meta=None):
        self.analysis = analysis
        self.analysis_instance = analysis()
        self.cli_args = cli_args
        self.request_args = request_args
        self.meta = meta or Meta
        self.emitted_messages = []

        Meta.fill_action_handlers(analysis)

        # initialize
        self.analysis_instance.init_databench()
        self.analysis_instance.set_emit_fn(self.emulate_emit_to_frontend)
        self.trigger('connect')
        self.trigger('args', [cli_args, request_args])
        self.trigger('connected')

    def emulate_emit_to_frontend(self, signal, message):
        self.emitted_messages.append((signal, message))

    def trigger(self, action_name, message='__nomessagetoken__', **kwargs):
        """Trigger an `on` callback.

        :param str action_name: Name of the action to trigger.
        :param message: Message.
        :param callback:
            A callback function when done (e.g.
            `~tornado.testing.AsyncTestCase.stop` in tests).
        :rtype: tornado.concurrent.Future
        """
        return self.meta.run_process(
            self.analysis_instance, action_name, message, **kwargs)
