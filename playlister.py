#!/usr/bin/python3
#
# playlister.py
# @author Jared Smith <jasmith79>
# @copyright 2017 Jared Smith
# @license MIT
# You should have received a copy of the software license with this work, the terms of which can
# be found at https://opensource.org/licenses/MIT
#
# Requires Python 3.5+. No other dependencies.
# Converts iTunes® plist xml files into universal formats like m3u, m3u8, and xspf.

import re
import urllib.request
import plistlib
import collections
import time

from os import path, listdir, sep
from functools import partial
from typing import List, Dict, Union, Any
from urllib.parse import unquote, quote
from unicodedata import normalize as uni_norm
from xml.sax.saxutils import escape as esc_xml
from argparse import ArgumentParser, Namespace

_STARTS_WITH_WIN_URI = re.compile(r"^/\w+:[\\/]{1}")

VERBOSE = []

XSPF_TRACK_TEMPLATE = """    <track>
      <location>{location}</location>
      <title>{title}</title>
      <creator>{artist}</creator>
      <album>{album}</album>
      <duration>{duration}</duration>
    </track>"""

XSPF_TEMPLATE = """<?xml version="1.0" encoding="UTF-8"?>
<playlist version="1" xmlns="http://xspf.org/ns/0/">
  <trackList>
{tracks}
  </trackList>
</playlist>
"""

M3U_TEMPLATE = """#EXTM3U
#name={name}
{tracks}
"""

M3U_TRACK_TEMPLATE = "#EXTINF:{0},{1} - {2}\n{3}"

MATCH_PATH = re.compile(
    r"^(?P<uri>file://)?" +
    r"(?P<path>(?:/?[A-Z]:)?[\\/]?(?:[-. \w]+[\\/])+)" +
    r"(?P<filename>\.?[^.\n]+?" +
    r"(?=\.(?P<extension>.+$)|$))?"
)

_STARTS_WITH_WIN_URI = re.compile(r"^/\w+:[\\/]{1}")

ITUNES_PATH = re.compile(
    r"[\\/]Users[\\/][\w\.\-]+[\\/]" + # windows and mac both do Users-delimiter-Username
    r"(?:My )?Music[\\/]iTunes[\\/]" + # windows uses 'My ', mac just Music
    r"iTunes(?: |%20)Media[\\/]" +     # optionally url encoded
    r"(?:Music[\\/])"                  # optional Music folder
)

class FileString(str):
    """Custom type for file strings. Does regex validation, adds some convenience methods. If the
    path is a directory it should end in a separator character \ or / depending on platform.
    Otherwise /foo/bar/makefile would be ambiguous, here it is (correctly in this case)
    interpreted as a path to a file without an extension. NOTE: when working with windows paths
    the backslashes will be automatically escaped."""
    def __new__(cls, user_path):
        # Skip the work of reconstructing it
        if isinstance(user_path, FileString):
            return user_path
        try:
            file_path = str.__new__(cls, user_path)
        except:
            # Will likely never see this, I can't think of anything that cannot be cast to str
            raise TypeError("Type {} with value {} cannot be converted to a FileString string.")

        match = re.match(MATCH_PATH, file_path)
        if not match:
            raise TypeError(
                "String {} does not match a file path or file uri format.".format(file_path)
            )

        uri, fpath, fname, ext = match.groups()

        # This covers for an inherent but as far as I know unavoidable problem with the regex
        if not uri and re.match(_STARTS_WITH_WIN_URI, fpath):
            raise TypeError(
                "Malformed windows file URI {}.".format(file_path)
            )

        # These don't need to be methods because strings are immutable
        file_path.path = fpath
        file_path.name = fname or ""
        file_path.extension = ext or ""
        file_path.is_uri = bool(uri)

        return file_path

    def exists(self):
        """Whether file/dir exists on the system, e.g. can be opened with 'open' or 'urlopen'.
        NOTE: not thread-safe. While exists may return True some other process could delete the
        file between the existence check and reading."""
        if path.isdir(self) or path.isfile(self):
            return True

        if not self.is_uri:
            return False

        try:
            with urllib.request.urlopen(self) as f:
                return True
        except:
            return False

# A few helper functions
def fmap(f, xs):
    return [f(x) for x in xs]

def pipe(*fs):
    """Forward function composition. Yes, I know mutation is evil. First function may be of
    any arity, all others must be unary."""
    def collect(*args, **kwargs):
        head, *tail = fs
        result = head(*args, **kwargs)
        for f in tail:
            result = f(result)
        return result
    return collect

def trail_slash(string: str):
    return string if string.endswith(sep) else string + sep

def glob_xml_files(user_path: FileString) -> List[str]:
    """Takes a path to a xml directory and returns a list containing all of the
    xml files in the directory"""
    if user_path.exists():
        files = [
            FileString(file) for file in (path.join(user_path, f) for f in listdir(user_path))
        ]
        return [
            f for f in files if f.extension == "xml" and f.exists() and not f.name.startswith(".")
        ]

    else:
        raise ValueError("Error: {} is not a directory".format(user_path))

normalize = partial(uni_norm, "NFC") # convert combining diacritical marks to combined form
escape_xspf_path = pipe(unquote, normalize, quote, esc_xml)

def init_parser():
    parser = ArgumentParser()
    parser.add_argument("target_path", help="path to the xml file or directory")
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
        default="m3u"
    )
    parser.add_argument(
        "-o",
        "--output-path",
        help="path for output, defaults to target_path with 'xml' replaced by --type"
    )
    parser.add_argument(
        "-m",
        "--music-path",
        help="path music files, defaults to the original iTunes® path"
    )

    return parser

def load_plist(file_path: FileString) -> Dict[str, Any]:
    """Takes plist xml file binary and returns a Dict of the contents."""
    if VERBOSE:
        print("Reading...".format(file_path))
    try:
        with open(file_path, "rb") as f:
            return plistlib.load(f)
    except:
        if VERBOSE:
            print("...not a valid iTunes playlist file. Skipping...")
        return {}

def extract_tracks(plist) -> List[Dict[str, str]]:
    """Takes a Dict loaded from plistlib and extracts the in-order tracks."""
    try:
        ordering = [str(a["Track ID"]) for a in plist["Playlists"][0]["Playlist Items"]]
        return [plist["Tracks"][track_id] for track_id in ordering]
    except KeyError:
        return []

def replace_music_path(music_path: str, track: Dict[str, str]) -> Dict[str, str]:
    """Takes a track record and changes the location to accurately reflect the new
    path instead of the iTunes path."""
    if music_path:
        track["Location"] = quote(ITUNES_PATH.sub(music_path, unquote(track.get("Location")[7:])))
    return track

def to_m3u(record: Dict[str, str]) -> str:
    """Converts a single track record into m3u format."""
    # [7:] drops the file:// Android doesn't like URIs here
    location = normalize(unquote(record.get("Location")))
    duration = int(record.get("Total Time")) // 1000 # m3u durations in seconds
    name = normalize(unquote(record.get("Name")))
    artist = normalize(unquote(
        record.get("Artist") or
        record.get("Album Artist") or
        record.get("Composer", "")
    ))

    return M3U_TRACK_TEMPLATE.format(duration, artist, name, location)

def to_xspf(record: Dict[str, str]) -> str:
    """Converts a single track record into xspf format."""
    location = "file://" + escape_xspf_path(record.get("Location"))
    duration = record.get("Total Time", "")
    album = esc_xml(record.get("Album", ""))
    name = esc_xml(record.get("Name", ""))
    artist = esc_xml(
        record.get("Artist") or
        record.get("Album Artist") or
        record.get("Composer", "")
    )

    return XSPF_TRACK_TEMPLATE.format(
        title=name,
        location=location,
        album=album,
        artist=artist,
        duration=duration
    )

CONVERSION_MAPPING = {
    "xspf": (XSPF_TEMPLATE, to_xspf),
    "m3u": (M3U_TEMPLATE, to_m3u),
    "m3u8": (M3U_TEMPLATE, to_m3u)
}

def playlister(
    target_path: str,
    music_path: str,
    list_type: str
) -> Any:
    if not target_path:
        raise ValueError("Must have target file/directory.")

    p = trail_slash(target_path) if path.isdir(target_path) else target_path
    tpath = FileString(p)
    mpath = FileString(trail_slash(music_path))
    tmpl, conversion_fn = CONVERSION_MAPPING[list_type]
    if tpath.name:
        files = [tpath]
    else:
        if VERBOSE:
            print("Scanning target for files...")

        files = glob_xml_files(tpath)
        if VERBOSE:
            print("...done. Found {} files.".format(str(len(files))))

    conv = pipe(
        load_plist,
        extract_tracks,
        partial(fmap, partial(replace_music_path, mpath)),
        partial(fmap, conversion_fn)
    )

    results = []
    for file in files:
        if VERBOSE:
            print("Converting file {}...".format(file))
        res = conv(file)
        if VERBOSE:
            print("...done.")
            if not res:
                print("...not able to convert file.".format(file))

        kwargs = {
            "tracks": "\n".join(res)
        }
        if list_type == "m3u" or list_type == "m3u8":
            kwargs["name"] = file.name
        results.append((file.name, tmpl.format(**kwargs)))

    return results

def main(args: Namespace) -> None:
    if args.verbose:
        start_time = time.time()
        VERBOSE.append(1)

    if args.output_path:
        opath = FileString(args.output_path).path
    else:
        p = trail_slash(target_path) if path.isdir(target_path) else target_path
        tpath = FileString(p)
        opath = tpath.path

    results = playlister(args.target_path, args.music_path, args.type)
    for name, contents in results:
        file_path = FileString(opath + name + "." + args.type)
        if contents:
            if VERBOSE:
                print("Writing file {}...".format(file_path))
            try:
                with open(file_path, "w") as f:
                    f.write(contents)
                if VERBOSE:
                    print("...done.")

            except IOError as e:
                if VERBOSE:
                    print("...cannot write, likely insufficient permissions.".format(file_path))
        else:
            if VERBOSE:
                print("No contents to write to file {}, skipping...")

    if VERBOSE:
        run_time = round(time.time() - start_time, 4)
        print("Finished. Converted {} files in {} seconds.".format(str(len(results)), run_time))
    return None

if __name__ == "__main__":
    main(init_parser().parse_args())