import logging
import tornado.gen

from .analysis_zmq import AnalysisZMQ
from .meta import Meta

log = logging.getLogger(__name__)


class MetaZMQ(Meta):
    """A Meta class that pipes all messages to ZMQ and back.

    The entire ZMQ interface of Databench is defined here and in
    :class`AnalysisZMQ`.

    """

    def __init__(self, name, executable, zmq_publish,
                 analysis_path, extra_routes, cmd_args=None):
        super(MetaZMQ, self).__init__(name, AnalysisZMQ,
                                      analysis_path, extra_routes, cmd_args)

        self.executable = executable
        self.zmq_publish = zmq_publish

    @tornado.gen.coroutine
    def run_process(self, analysis, action_name, message='__nomessagetoken__'):
        """Executes an process in the analysis with the given message.

        It also handles the start and stop signals in case a process_id
        is given.
        """

        if action_name == 'connect':
            analysis.on_connect(self.executable, self.zmq_publish)

        while not analysis.zmq_handshake:
            yield tornado.gen.sleep(0.1)

        log.debug('sending action {}'.format(action_name))
        analysis.zmq_send({'signal': action_name, 'load': message})

        if action_name == 'disconnected':
            # Give kernel time to process disconnected message.
            yield tornado.gen.sleep(0.1)
            analysis.on_disconnected()
