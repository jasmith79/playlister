"""
.. py:module:: files
    :platform: Unix, Windows
    :synopsis: File operations for playlister, e.g. opens
        and parses XML/plist playlist files.
"""

import plistlib

import pathlib
from typing import Optional, Dict, Any, List, Tuple


def glob_xml_files(directory: pathlib.Path) -> List[pathlib.Path]:
    """Takes a path to a xml directory and returns a list containing all of the
        xml files in the directory.

        :param directory: directory to glob.
        :returns: List of file names.
        :raises: OSError
    """

    if directory.exists() and directory.is_dir():
        return [
            p for p in directory.glob("*.xml") if not p.name.startswith(".")
        ]

    else:
        raise OSError("Error: {} is not a directory".format(directory))


def extract_tracks(plist: Dict) -> List[Dict[str, str]]:
    """Takes a Dict loaded from plistlib and extracts the in-order tracks.

        :param plist: the xml plist parsed into a Dict.
        :returns: a list of the extracted track records.
    """
    try:
        ordering = [
            str(a["Track ID"]) for a in plist["Playlists"][0]["Playlist Items"]
        ]
        return [plist["Tracks"][track_id] for track_id in ordering]

    except KeyError:
        return []


def load_plist(
    file: pathlib.Path,
    verbose: Optional[bool] = False
) -> List[Dict[str, str]]:
    """Takes plist xml file binary and returns a List of the track records.

        :param file: the file to load
        :param verbose: toggles verbose output.
        :returns: a list of the track records.
    """

    if verbose:
        print("Reading...".format(file.resolve()))
    try:
        with file.open("rb") as f:
            return extract_tracks(plistlib.load(f))

    # Don't care here what the problem is: if the file doesn't exist
    # or isn't the right format, either way can't do anything useful.
    except Exception as e:
        if verbose:
            print("...not a valid iTunes playlist file. Skipping...")
        return []
