"""
.. py:module:: m3u
    :platform: Unix, Windows
    :synopsis: Defines all m3u-related operations for playlister.
"""

from urllib.parse import unquote
from typing import Dict, List

from playlister.playlister_utils import normalize

M3U_TEMPLATE = """#EXTM3U
#name={name}
{tracks}
"""

M3U_TRACK_TEMPLATE = "#EXTINF:{length},{artist} - {title}\n{path}"


def to_m3u_track(record: Dict[str, str]) -> str:
    """Converts a single track record into m3u format. Need the
        normalization to fix the way Apple handles e.g. combining
        diacriticals.

        :param record: the track record to convert to m3u format.
        :returns: the m3u-formatted string with the track data.
    """

    location = normalize(unquote(record.get("Location")))

    # m3u duration in seconds, not ms
    duration = int(record.get("Total Time")) // 1000
    name = normalize(unquote(record.get("Name")))
    artist = normalize(unquote(
        record.get("Artist") or
        record.get("Album Artist") or
        record.get("Composer", "")
    ))
    # print("Location {}".format(location))
    return M3U_TRACK_TEMPLATE.format(
        length=duration,
        artist=artist,
        title=name,
        path=location
    )


def to_m3u_list(list_name: str, tracks: List[str]) -> str:
    """Converts a list of serialized m3u tracks into a playlist.

        :param list_name: name of the playlist.
        :param tracks: list of m3u tracks to include.
        :returns: the playlist as a string.
    """

    return M3U_TEMPLATE.format(name=list_name, tracks="\n".join(tracks))
