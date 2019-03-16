"""
.. py:module:: test_cli
    :platform: Unix, Windows
    :synopsis: tests the cli interface for the playlister utility.
"""

import pytest

from .context import cli


class TestCLI(object):
    """Groups the tests of the command line argument parser."""

    def test_basic_parse(self):
        """Parses a basic set of inputs."""

        args = cli.parse_args([
            "/home/xml",
            "--verbose",
            "-t", "xspf",
            "-m", "/foo/bar",
            "-o", "/bar/foo"
        ])

        assert(str(args["music_path"]) == "/foo/bar")
        assert(str(args["output_path"]) == "/bar/foo")
        assert(str(args["target_path"]) == "/home/xml")
        assert(args["verbose"] == True)
        assert(args["list_type"] == "xspf")

    def test_defaults(self):
        """Tests the default options"""

        args = cli.parse_args(["/home/xml"])

        assert(args["music_path"] is None)
        assert(str(args["output_path"]) == "/home/m3u")
        assert(str(args["target_path"]) == "/home/xml")
        assert(args["verbose"] == False)
        assert(args["list_type"] == "m3u")
