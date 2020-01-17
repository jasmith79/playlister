"""
.. py:module:: app
    :platform: Unix, Windows
    :synopsis: main file for the playlister utility.
"""

import sys
import re
import os.path

from time import time
from datetime import timedelta
from urllib.parse import unquote, quote
from pathlib import Path
from typing import Dict, Optional, List, Tuple
from functools import partial

from cli import parse_args
from files import glob_xml_files, load_plist
from playlister_utils import pipe
from m3u import to_m3u_track, to_m3u_list
from xspf import to_xspf_track, to_xspf_list

start = time()

ITUNES_PATH = re.compile(
    # windows and mac both do Users-delimiter-Username
    r"[\\/]Users[\\/][\w\.\-]+[\\/]" +

    # windows uses 'My ', mac just Music
    r"(?:My )?Music[\\/]iTunes[\\/]" +

    # optionally url encoded
    r"iTunes(?: |%20)Media[\\/]" +

    # optional Music folder
    r"(?:Music[\\/])"
)


class NoTargetPathError(Exception):
    """Error raised when no target path is passed."""

    pass


class UnknownOutputFormatError(Exception):
    """Error raised for unknown playlist type"""

    pass


def replace_music_path(
    music_path: Path,
    track: Dict[str, str]
) -> Dict[str, str]:
    """Takes a track record and changes the location to accurately
        reflect the new path instead of the iTunes path.

        :param music_path: the path to the music files on the target machine.
        :param track: the record for the track to update.
        :returns: the updated track record.
    """

    # unquoted = unquote(track.get("Location", "")[7:]) + os.path.sep
    # subbed = ITUNES_PATH.sub(str(music_path).replace("\\", "\\\\"), unquoted)
    # quoted = quote(subbed)
    # track["Location"] = quoted

    # Android doesn't like file urls, chop file://
    unquoted = unquote(track.get("Location", "")[7:])
    oldPath = re.sub(ITUNES_PATH, "", unquoted)
    newPath = os.path.join(music_path, oldPath)
    track["Location"] = quote(str(newPath))

    return track


def playlister(
    target_path: Path,
    output_path: Path,
    list_type: str,
    music_path: Optional[Path] = None,
    verbose: Optional[bool] = False
) -> List[Tuple[Path, str]]:
    """Main function for altering playlists.

        :param target_path: the path to the xml file/directory.
        :param output_path: the path to write the modified lists to.
        :param list_type: the list type, one of xspf, m3u, m3u8.
        :param music_path: the path to the music files, e.g. if converting
            lists meant to be played on another device.
        :param verbose: toggles verbose output.
        :returns: List of tuples in the form (output_filepath, contents)
        :raises: NoTargetPathError, OSError, UnknownOutputFormatError
    """

    output = None
    conversions = []

    if not target_path:
        raise NoTargetPathError("Must have target file/directory.")

    if target_path.is_dir():
        if verbose:
            print("{} is a directory. Scanning for xml files...".format(
                str(target_path)
            ))

        orig_files = glob_xml_files(target_path)
        num_files = len(orig_files)
        if not output_path.is_dir:
            raise OSError("{} is not a directory.".format(str(output_path)))

        if verbose:
            print("done. Found {} xml files.".format(num_files))

    else:
        orig_files = [target_path]
        if output_path.is_file():
            output = [output_path]

    if music_path:
        conversions.append(
            partial(replace_music_path, music_path)
        )

    if list_type == "m3u" or list_type == "m3u8":
        conversions.append(to_m3u_track)
        convert_list = to_m3u_list

    elif list_type == "xspf":
        conversions.append(to_xspf_track)
        convert_list = to_xspf_list

    else:
        raise UnknownOutputFormatError(
            "Unknown list type {}.".format(list_type)
        )

    convert = pipe(load_plist, partial(map, pipe(*conversions)))

    converted = []
    for i, orig_file in enumerate(orig_files):
        if verbose:
            print("Converting {}, {} of {}".format(
                orig_file.name,
                i + 1,
                num_files
            ))

        list_name = orig_file.name.split(".")[0]

        if output:
            new_file = output[i]

        else:
            new_file = Path(os.path.join(
                output_path,
                "{}.{}".format(list_name, list_type)
            ))

        if verbose:
            print("Converting tracks...")

        contents = convert_list(list_name, convert(orig_file))
        if verbose:
            print("done.")

        converted.append((new_file, contents))

    return converted


def main():
    cli_args = parse_args(sys.argv[1:])
    verbose = cli_args["verbose"]
    converted = playlister(**cli_args)
    num_files = len(converted)

    for i, data in enumerate(converted):
        path, contents = data
        if verbose:
            print("Writing {} of {}: {}...".format(
                i + 1,
                num_files,
                str(path)
            ))

        with path.open("w") as f:
            f.write(contents)

            if verbose:
                print("done.")

    return 0


if __name__ == "__main__":
    sys.exit(main())
