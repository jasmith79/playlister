"""
.. py:module:: test_cli
    :platform: Unix, Windows
    :synopsis: tests the cli interface for the playlister utility.
"""

import os.path

import pytest

from .context import cli

test_dir = os.path.dirname(os.path.realpath(__file__))
root_dir = os.path.sep.join(test_dir.split(os.path.sep)[:-1])
resource_dir = os.path.join(root_dir, "resources")


class TestCLI(object):
    """Groups the tests of the command line argument parser."""

    def test_basic_parse(self):
        """Parses a basic set of inputs."""

        args = cli.parse_args([
            resource_dir,
            "--verbose",
            "-t", "xspf",
            "-m", "/foo/bar",
            "-o", "/bar/foo"
        ])

        assert(str(args["music_path"]) == "/foo/bar")
        assert(str(args["output_path"]) == "/bar/foo")
        assert(str(args["target_path"]) == resource_dir)
        assert(args["verbose"] == True)
        assert(args["list_type"] == "xspf")

    def test_defaults(self):
        """Tests the default options"""

        args = cli.parse_args([resource_dir])

        assert(args["music_path"] is None)
        assert(str(args["output_path"]) == resource_dir)
        assert(str(args["target_path"]) == resource_dir)
        assert(args["verbose"] == False)
        assert(args["list_type"] == "m3u")
