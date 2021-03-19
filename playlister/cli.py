"""
.. py:module:: cli
    :platform: *nix, Windows
    :synopsis: Defines the command-line interface for the playlister utility.
"""

import subprocess
import os.path

from argparse import ArgumentParser, ArgumentError
from typing import List, Dict, Optional
from pathlib import Path

# from __version__ import version
__version__ = "1.1.0"


def init_default_parser() -> ArgumentParser:
    """Creates the default argument parser.

        :returns: an ArgumentParser with the default options.
    """

    version = "1.1.0"
    parser = ArgumentParser()
    parser.add_argument(
        "target_path",
        help="path to the xml file or directory",
        type=Path
    )

    parser.add_argument(
        "-v", "--verbose",
        help="Verbose output",
        dest="verbose",
        action="store_true"
    )

    parser.add_argument(
        "-t",
        "--type",
        help="type of output list, defaults to m3u.",
        choices=["m3u", "m3u8", "xspf"],
        default="m3u",
        dest="list_type"
    )

    parser.add_argument(
        "-o",
        "--output-path",
        help="path for output, defaults to target_path with 'xml' replaced by --type",
        type=Path
    )

    parser.add_argument(
        "-m",
        "--music-path",
        help="path music files, defaults to the original iTunes® path",
        type=Path
    )

    parser.add_argument(
        "--version",
        help="Current version.",
        action="version",
        version="Playlister {}".format(version)
    )

    return parser


def parse_args(
    args: List[str],
    parser: Optional[ArgumentParser] = init_default_parser()
) -> Dict:
    """Parses a list of CLI arguments into a Dict.

        :param args: the list of arguments to be parsed, e.g. sys.argv
        :param parser: the parser to use, defaults to the default parser.
        :returns: the parsed args as a Dict.
        :raises: ArgumentError, OSError
    """

    ns = parser.parse_args(args)
    parsed_args = ns.__dict__

    if not ns.output_path:
        parsed_args["output_path"] = Path(
            str(ns.target_path).replace("xml", ns.list_type)
        )

    if not ns.target_path.exists():
        raise OSError("{} does not exist".format(ns.target_path))

    return parsed_args
