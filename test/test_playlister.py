"""
.. py:module:: test_playlister
    :platform: Unix, Windows
    :synopsis: Integration test: tests an actual list conversion,
        start to finish.
"""

import os.path

from pathlib import Path

from .context import playlister, cli

test_dir = os.path.dirname(os.path.realpath(__file__))
root_dir = os.path.sep.join(test_dir.split(os.path.sep)[:-1])
resource_dir = os.path.join(root_dir, "resources")

with open(os.path.join(resource_dir, "Buffett.m3u")) as f:
    m3u_result = f.read()

with open(os.path.join(resource_dir, "Buffett.xspf")) as f:
    xspf_result = f.read()


class TestPlaylister(object):

    def test_m3u(self):
        args = [
            resource_dir,
            "-t", "m3u",
            "-o", resource_dir,
            "-m", os.path.join(os.path.sep, "home", "jsmith", "Music")
        ]

        path, contents = playlister.playlister(**cli.parse_args(args))[0]
        assert(path == Path(os.path.join(resource_dir, "Buffett.m3u")))
        assert(contents == m3u_result)

    def test_xspf(self):
        args = [
            resource_dir,
            "-t", "xspf",
            "-o", resource_dir,
            "-m", os.path.join(os.path.sep, "home", "jsmith", "Music")
        ]

        path, contents = playlister.playlister(**cli.parse_args(args))[0]
        assert(path == Path(os.path.join(resource_dir, "Buffett.xspf")))
        assert(contents == xspf_result)
