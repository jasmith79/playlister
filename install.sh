#!/bin/bash

wd=$(pwd)
rm -f /usr/local/bin/playlister
ln -s $wd/playlister.py /usr/local/bin/playlister
