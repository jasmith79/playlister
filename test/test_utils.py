"""
.. py:module:: test_utils
    :platform: Unix, Windows
    :synopsis: tests miscellaneous utilites for playlister.
"""

import pytest

from .context import utils


class TestUtils(object):
    """Groups the utilities file tests."""

    def test_pipe(self):
        """Tests function piping"""

        def add3(n: int) -> int:
            return n + 3

        def times2(n: int) -> int:
            return n * 2

        add3times2 = utils.pipe(add3, times2)
        assert(add3times2(3) == 12)
