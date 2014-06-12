"""Analysis module for Databench."""

from flask import Blueprint, render_template

import databench.signals


LIST_ALL = []

class Analysis(object):
    """Databench's analysis class. 

    An optional :class:`databench.Signals` instance and :class:`flask.Blueprint`
    can be dependency-injected, however that should not be necessary for
    standard use cases.

    Args:
        name (str): Name of this analysis. If ``signals`` is not specified, this
            also becomes the namespace for the Socket.IO connection and has
            to match the frontend's :js:class:`Databench` ``name``.
        import_name (str): Usually the file name ``__name__`` where this
            analysis is instantiated.
        signals (optional): Inject an instance of :class:`databench.Signals`.
        blueprint (optional): Inject an instance of a :class:`flask.Blueprint`.

    """

    def __init__(
            self,
            name,
            import_name,
            signals=None,
            blueprint=None
    ):
        LIST_ALL.append(self)
        self.name = name
        self.import_name = import_name

        if not signals:
            self.signals = databench.signals.Signals(name)
        else:
            self.signals = signals

        if not blueprint:
            self.blueprint = Blueprint(
                name,
                import_name,
                template_folder='templates',
                static_folder='static',
            )
        else:
            self.blueprint = blueprint

        @self.blueprint.route('/')
        def render_index():
            """Renders the main analysis frontend template."""
            return render_template(self.name+'.html')
