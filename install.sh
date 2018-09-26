#!/bin/bash

wd=$(pwd)
sudo rm -f /usr/local/bin/playlister
sudo ln -s $wd/playlister.py /usr/local/bin/playlister
