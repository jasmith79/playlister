"""
.. py:module:: test_xspf
    :platform: Unix, Windows
    :synopsis: tests the xspf-related functions for the playlister utility.
"""

import pytest

from .context import xspf


class TestXSPF(object):
    """Groups the tests of the xspf-related functions"""

    def test_to_xspf_track(self):
        """Tests converting a track record to an xspf string"""

        test_track = {
            "Location": "/foo/bar/baz.mp3",
            "Total Time": "192000",
            "Name": "testing123",
            "Artist": "Kool Kat",
            "Album": "For the road"
        }

        result = """    <track>
      <location>file:///foo/bar/baz.mp3</location>
      <title>testing123</title>
      <creator>Kool Kat</creator>
      <album>For the road</album>
      <duration>192000</duration>
    </track>"""

        assert(xspf.to_xspf_track(test_track) == result)