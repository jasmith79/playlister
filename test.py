import re

from playlister import extract_tracks, replace_music_path, to_m3u, to_xspf
from playlister import glob_xml_files, playlister, load_plist, FileString
from filecmp import cmp
from shutil import rmtree
from os import listdir, makedirs

# I know I know, regexes aren't powerful enough to process CFGs. This is a simple match. Deal.
XML_LOC = re.compile(r"<location>([\w\s\-\.%/\\:]+)</location>")
XML_TAGS = re.compile(r"<(\w+)>")
M3U_TRACK = """#EXTINF:205,Jimmy Buffett - Son of a Son of a Sailor
/foo/bar/Jimmy Buffett/Son of a Son of a Sailor/01 Son of a Son of a Sailor.m4a"""

def clear_out():
    rmtree("./output/", ignore_errors=True)
    makedirs('./output', exist_ok=True)
    if len(listdir("./output")) != 0:
        raise AssertionError("Output directory should be empty!")

clear_out()

# glob_xml_files
xmls = glob_xml_files(FileString("./resources/"))
assert len(xmls) == 1
assert xmls[0] == "./resources/Buffett.xml"

# load_plist
plist = load_plist(xmls[0])
assert plist.get("Playlists")

# extract_tracks
track = extract_tracks(plist)[0]
assert track.get("Name") == "Son of a Son of a Sailor"

# replace_music_path
trak = replace_music_path("/foo/bar/", track)
assert trak.get("Location") == "/foo/bar/Jimmy%20Buffett/Son%20of%20a%20Son%20of%20a%20Sailor/01%20Son%20of%20a%20Son%20of%20a%20Sailor.m4a"

# convert xspf
xspf = to_xspf(trak)
# NOTE, assumes no xml special characters got escaped
matches = re.findall(XML_LOC, xspf)
assert matches
assert matches[0] == "file://" + trak.get("Location")
tags = re.findall(XML_TAGS, xspf)
assert set(tags) == set(("title","location","creator","duration","album","track"))

# convert m3u, short enough we'll just compare to expected output directly
m3u = to_m3u(trak)
assert M3U_TRACK == m3u

# playlister
m3u_list = playlister("./resources/", "/home/jsmith/Music/", "m3u")[0][1].strip()
with open("./resources/Buffett.m3u") as f:
    assert m3u_list == f.read().strip()

xspf_list = playlister("./resources/", "/home/jsmith/Music", "xspf")[0][1].strip()
with open("./resources/Buffett.xspf") as f:
    assert xspf_list == f.read().strip()

def test_wrong_file():
    pass

def test_missing_file():
    pass

def test_no_xml():
    pass
