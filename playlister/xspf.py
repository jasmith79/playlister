"""
.. py:module:: xspf
    :platform: Unix, Windows
    :synopsis: Defines all xspf-related operations for playlister.
"""

from urllib.parse import unquote, quote
from unicodedata import normalize as uni_norm
from xml.sax.saxutils import escape as esc_xml
from typing import Dict, List

from playlister_utils import pipe, normalize

escape_xspf_path = pipe(unquote, normalize, quote, esc_xml)

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


def to_xspf_track(record: Dict[str, str]) -> str:
    """Converts a single track record into xspf format.

        :param record: the track record to convert.
        :returns: the track formatted as an xspf xml entry.
    """
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


def to_xspf_list(list_name: str, tracks: List[str]) -> str:
    """Converts a list of serialized xspf tracks into a playlist.

        :param list_name: name of the playlist.
        :param tracks: list of xspf tracks to include.
        :returns: the playlist as a string.
    """

    return XSPF_TEMPLATE.format(name=list_name, tracks="\n".join(tracks))
