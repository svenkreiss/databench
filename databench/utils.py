"""Utility functions."""

import base64
import io

try:
    import numpy as np
except ImportError:
    np = None


def json_encoder_default(obj):
    """Handle more data types than the default JSON encoder.

    Specifically, it treats a ``set`` and a numpy array like a ``list``.

    Example usage: ``json.dumps(obj, default=json_encoder_default)``
    """
    if np is not None:
        if isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.float):
            return float(obj)

    if isinstance(obj, set):
        return list(obj)
    elif obj.__class__.__name__ == 'DatastoreList':
        return list(obj)
    elif obj.__class__.__name__ == 'DatastoreDict':
        return dict(obj)
    elif hasattr(obj, 'tolist') and hasattr(obj, '__iter__'):
        # for np.array
        return obj.tolist()

    return obj


def fig_to_src(figure, image_format='png', dpi=80):
    """Convert a matplotlib figure to an inline HTML image.

    :param matplotlib.Figure figure: Figure to display.
    :param str image_format: png (default) or svg
    :param int dpi: dots-per-inch for raster graphics.
    :rtype: str
    """
    if image_format == 'png':
        f = io.BytesIO()
        figure.savefig(f, format=image_format, dpi=dpi)
        f.seek(0)
        return png_to_src(f.read())

    elif image_format == 'svg':
        f = io.StringIO()
        figure.savefig(f, format=image_format, dpi=dpi)
        f.seek(0)
        return svg_to_src(f.read())


def png_to_src(png):
    """Convert a PNG string to a format that can be passed into a src.

    :rtype: str
    """
    return 'data:image/png;base64,' + base64.b64encode(png).decode()


def svg_to_src(svg):
    """Convert an SVG string to a format that can be passed into a src.

    :rtype: str
    """
    return 'data:image/svg+xml;utf8,' + svg
