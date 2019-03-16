"""
.. py:module:: test_files
    :platform: Unix, Windows
    :synopsis: tests the file operations for the playlister utility.
"""

import os.path

from unittest import mock
from datetime import datetime
from io import BytesIO

import pytest

from test.context import files


class TestFiles(object):
    """Groups the tests for the file operations module.
        ..NOTE: although there are three functions in this module,
            two of them are paper-thin wrappers over standard
            library functions, so we"re not bothering to test them.
    """

    def test_load_plist(self):
        """Tests converting a plist file to a list of track
            records as dicts.
        """

        test_plist = """<?xml version="1.0" encoding="UTF-8"?>
            <!DOCTYPE plist PUBLIC "-//Apple Computer//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
            <plist version="1.0">
            <dict>
            	<key>Major Version</key><integer>1</integer>
            	<key>Minor Version</key><integer>1</integer>
            	<key>Date</key><date>2016-08-22T14:31:48Z</date>
            	<key>Application Version</key><string>12.4.3.1</string>
            	<key>Features</key><integer>5</integer>
            	<key>Show Content Ratings</key><true/>
            	<key>Music Folder</key><string>file:///Users/jared/Music/iTunes/iTunes%20Media/</string>
            	<key>Library Persistent ID</key><string>2EE7826E137BE07F</string>
            	<key>Tracks</key>
            	<dict>
            		<key>5230</key>
            		<dict>
            			<key>Track ID</key><integer>5230</integer>
            			<key>Name</key><string>Son of a Son of a Sailor</string>
            			<key>Artist</key><string>Jimmy Buffett</string>
            			<key>Album Artist</key><string>Jimmy Buffett</string>
            			<key>Composer</key><string>Jimmy Buffett</string>
            			<key>Album</key><string>Son of a Son of a Sailor</string>
            			<key>Genre</key><string>Rock</string>
            			<key>Kind</key><string>Purchased AAC audio file</string>
            			<key>Size</key><integer>7839010</integer>
            			<key>Total Time</key><integer>205250</integer>
            			<key>Disc Number</key><integer>1</integer>
            			<key>Disc Count</key><integer>1</integer>
            			<key>Track Number</key><integer>1</integer>
            			<key>Track Count</key><integer>9</integer>
            			<key>Year</key><integer>1978</integer>
            			<key>Date Modified</key><date>2014-01-21T23:44:49Z</date>
            			<key>Date Added</key><date>2014-01-21T23:43:47Z</date>
            			<key>Bit Rate</key><integer>256</integer>
            			<key>Sample Rate</key><integer>44100</integer>
            			<key>Play Count</key><integer>12</integer>
            			<key>Play Date</key><integer>3538303254</integer>
            			<key>Play Date UTC</key><date>2016-02-14T19:00:54Z</date>
            			<key>Skip Count</key><integer>2</integer>
            			<key>Skip Date</key><date>2016-02-14T18:57:29Z</date>
            			<key>Release Date</key><date>1978-03-01T00:00:00Z</date>
            			<key>Normalization</key><integer>328</integer>
            			<key>Artwork Count</key><integer>1</integer>
            			<key>Sort Album</key><string>Son of a Son of a Sailor</string>
            			<key>Sort Artist</key><string>Jimmy Buffett</string>
            			<key>Sort Name</key><string>Son of a Son of a Sailor</string>
            			<key>Persistent ID</key><string>E91DEF8ED62D53CD</string>
            			<key>Track Type</key><string>File</string>
            			<key>Purchased</key><true/>
            			<key>Location</key><string>file:///Users/jared/Music/iTunes/iTunes%20Media/Music/Jimmy%20Buffett/Son%20of%20a%20Son%20of%20a%20Sailor/01%20Son%20of%20a%20Son%20of%20a%20Sailor.m4a</string>
            			<key>File Folder Count</key><integer>5</integer>
            			<key>Library Folder Count</key><integer>1</integer>
            		</dict>
                </dict>
                <key>Playlists</key>
            	<array>
            		<dict>
            			<key>Name</key><string>Buffett</string>
            			<key>Description</key><string></string>
            			<key>Playlist ID</key><integer>29699</integer>
            			<key>Playlist Persistent ID</key><string>6655220441011185</string>
            			<key>All Items</key><true/>
            			<key>Playlist Items</key>
            			<array>
            				<dict>
            					<key>Track ID</key><integer>5230</integer>
            				</dict>
                        </array>
            		</dict>
            	</array>
            </dict>
            </plist>
        """.encode()

        expected = [{
            "Album": "Son of a Son of a Sailor",
            "Album Artist": "Jimmy Buffett",
            "Artist": "Jimmy Buffett",
            "Artwork Count": 1,
            "Bit Rate": 256,
            "Composer": "Jimmy Buffett",
            "Date Added": datetime(2014, 1, 21, 23, 43, 47),
            "Date Modified": datetime(2014, 1, 21, 23, 44, 49),
            "Disc Count": 1,
            "Disc Number": 1,
            "File Folder Count": 5,
            "Genre": "Rock",
            "Kind": "Purchased AAC audio file",
            "Library Folder Count": 1,
            "Location": "file:///Users/jared/Music/iTunes/iTunes%20Media/Music/Jimmy%20Buffett/Son%20of%20a%20Son%20of%20a%20Sailor/01%20Son%20of%20a%20Son%20of%20a%20Sailor.m4a",
            "Name": "Son of a Son of a Sailor",
            "Normalization": 328,
            "Persistent ID": "E91DEF8ED62D53CD",
            "Play Count": 12,
            "Play Date": 3538303254,
            "Play Date UTC": datetime(2016, 2, 14, 19, 0, 54),
            "Purchased": True,
            "Release Date": datetime(1978, 3, 1, 0, 0),
            "Sample Rate": 44100,
            "Size": 7839010,
            "Skip Count": 2,
            "Skip Date": datetime(2016, 2, 14, 18, 57, 29),
            "Sort Album": "Son of a Son of a Sailor",
            "Sort Artist": "Jimmy Buffett",
            "Sort Name": "Son of a Son of a Sailor",
            "Total Time": 205250,
            "Track Count": 9,
            "Track ID": 5230,
            "Track Number": 1,
            "Track Type": "File",
            "Year": 1978
        }]

        mock_file = BytesIO(test_plist)

        path_mock = mock.MagicMock()
        path_mock.open.return_value.__enter__.return_value = mock_file

        assert(files.load_plist(path_mock) == expected)
