"""
.. py:module:: test_m3u
    :platform: Unix, Windows
    :synopsis: tests the m3u-related functions for the playlister utility.
"""

import pytest

from .context import m3u


class TestM3U(object):
    """Groups the tests of the m3u-related functions"""

    def test_to_m3u_track(self):
        """Tests converting a track record dict into a m3u string."""

        test_track = {
            "Location": "/foo/bar/baz.mp3",
            "Total Time": "192000",
            "Name": "testing123",
            "Artist": "Kool Kat"
        }

        result = "#EXTINF:192,Kool Kat - testing123\n/foo/bar/baz.mp3"
        assert(m3u.to_m3u_track(test_track) == result)