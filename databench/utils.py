"""Utility functions."""

import base64
import io

try:
    import numpy as np
except ImportError:
    np = None


def sanitize_message(m):
    if isinstance(m, int) or isinstance(m, float) or \
       (np is not None and (isinstance(m, np.integer) or
                            isinstance(m, np.float))):
        if m != m:
            m = 'NaN'
        elif m == float('inf'):
            m = 'inf'
        elif m == float('-inf'):
            m = '-inf'
    elif isinstance(m, list):
        for i, e in enumerate(m):
            m[i] = sanitize_message(e)
    elif isinstance(m, dict):
        for i in m:
            m[i] = sanitize_message(m[i])
    elif isinstance(m, (set, tuple)):
        m = [sanitize_message(e) for e in m]
    elif hasattr(m, 'tolist') and hasattr(m, '__iter__'):  # for np.array
        m = [sanitize_message(e) for e in m]
    return m


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
