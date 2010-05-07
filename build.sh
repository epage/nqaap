#!/bin/sh

rm -r ~/nqaap;
svn export http://www.pengworld.com/python/n900/Audiobook/nqaap/ ~/nqaap
chmod +x ~/nqaap/src/opt/Nqa-Audiobook-player/nqaap.py
python ~/nqaap/build_nqaap.py

