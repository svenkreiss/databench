import databench
import unittest

import matplotlib
matplotlib.use('agg')
import matplotlib.pyplot as plt  # noqa: F401


class TestUtils(unittest.TestCase):
    def setUp(self):
        self.figure = plt.figure()
        ax = self.figure.add_subplot(1, 1, 1)
        ax.plot([1, 2, 3, 4])

    def test_png(self):
        src = databench.utils.fig_to_src(self.figure, 'png')
        self.assertEqual(src[:43],
                         'data:image/png;base64,iVBORw0KGgoAAAANSUhEU')

    def test_svg(self):
        src = databench.utils.fig_to_src(self.figure, 'svg')
        self.assertEqual(src[:43],
                         'data:image/svg+xml;utf8,<?xml version="1.0"')
