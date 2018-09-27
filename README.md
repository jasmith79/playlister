# Playlister

A utility for converting iTunes® playlists to various open formats. Note, although the usage tutorial
below tries to be as hand-holdy as possible (possibly to the point of being obnoxious about it), I
reasonably expect users to know how to navigate the filesystem, discovering for instance the full
path to where their music files are stored, etc. etc. If you're a more advanced computer user, just
use the `-h` or `--help` flags to see the usage.

## Requirements

Requires Python 3.5+. If you are on the current Ubuntu LTS (16.04) or any of its derivatives you
likely meet this requirement. Any other linux distros will have to check. Installing Python on
Mac or Windows is beyond the scope of this document, but not particularly difficult.

## Formats

Possible output formats are .m3u, .m3u8, and .xspf.

* m3u: m3u format, this is the default used by most Android® and many Windows music players.
* m3u8: m3u format but utf-8 encoded. **NOTE:** because of the needs of the Android® players which
cannot read .m3u8 files, there is no difference between the m3u and m3u8 outputs other than the
file extensions.
* xspf: XSPF format, an actual standardized open format that is the default for VLC.

## Installing

Currently, just clone the repo here at GitHub®. If you're on Linux or Mac just cd into the directory and run `./install.sh` (installs to `/usr/local/bin`). You can of course skip it link the file somewhere else in your $PATH. I will eventually get around to writing a Windows installer.

## Exporting the iTunes® lists

On your Mac select a playlist and go to File -> Library -> Export Playlist. Be sure to select the
.xml option, as that's the one Playlister knows how to work with. Repeat for all the playlists your
want to convert and put them all in a folder, preferably titled "xml".

## Using Playlister

Fire up the Terminal app on your platform of choice. 
type

`playlister /path/to/exported/itunes/playlists/xml/ -v`

and watch a bunch of stuff get printed to the terminal while it does its thing. Now you can open
your playlists in a program that has no knowledge of iTunes® format and play them. If you want to
move your playlists to a different device, you'll need to know where music is stored on the device.
On most operating system there will be a Music directory, and its where you should put your music
files. On Windows® its typically in `C:\Users\YourUserName\Documents\Music`, linux it's typically
`/home/YourUserName/Music`, and Android® it's not very standardized, you'll have to use a file
browser to figure it out. Once you've got it, add the following to the command above

`-m /path/to/music/files/on/device/`

and run it again. To change the output to m3u8 or xspf add `-t m3u8` or `-t xspf`. To specify where
the converted playlists are written to you can specify an output path like `-o ~/Desktop/Playlists/`
and it shall be done.
