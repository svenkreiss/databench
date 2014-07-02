"""Analysis module for Databench."""

from flask import Blueprint, render_template

from .signals import Signals


LIST_ALL = []


class Analysis(object):
    """Databench's analysis class.

    This class uses instances of :class:`databench.Signals` and
    :class:`flask.Blueprint` with default configurations. For advanced use
    cases, you can change those settings (e.g. folder name for ``templates``)
    by creating a new class with a modified constructor that inherits from
    this class.

    Args:
        name (str): Name of this analysis. If ``signals`` is not specified,
            this also becomes the namespace for the Socket.IO connection and
            has to match the frontend's :js:class:`Databench` ``name``.
        import_name (str): Usually the file name ``__name__`` where this
            analysis is instantiated.
        description (str): Usually the ``__doc__`` string of the analysis.

    """

    def __init__(
            self,
            name,
            import_name,
            description=None
    ):
        LIST_ALL.append(self)
        self.show_in_index = True

        self.name = name
        self.import_name = import_name
        self.description = description

        self.signals = Signals(name)
        self.blueprint = Blueprint(
            name,
            import_name,
            template_folder='templates',
            static_folder='static',
        )

        self.blueprint.add_url_rule('/', 'render_index', self.render_index)

    def render_index(self):
        """Renders the main analysis frontend template."""
        return render_template(
            self.name+'.html',
            analysis_description=self.description
        )
