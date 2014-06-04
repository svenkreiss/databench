"""Analysis class for Databench."""

from flask import Blueprint, render_template

import databench.signals


LIST_ALL = []

class Analysis(object):
    """Databench's analysis class."""

    def __init__(
            self,
            name,
            import_name,
            signals=None,
            blueprint=None
    ):
        """An optional Databench Signals object and Flask Blueprint can
        be dependency-injected."""

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
