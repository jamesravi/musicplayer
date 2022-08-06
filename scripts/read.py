# Copyright (C) 2022 James Ravindran
# SPDX-License-Identifier: AGPL-3.0-or-later

from tinydb import TinyDB
from mutagen.mp3 import MP3
import mutagen
import os

import sys
sys.path.append("..")
from get_music_path import get_music_path

music_path = str(get_music_path())

lengths = {}

def getlength(name):
    if name in lengths:
        return lengths[name]
    try:
        totallength = MP3(music_path+"\\"+name).info.length
    except mutagen.MutagenError:
        totallength = None
    lengths[name] = totallength
    return totallength

db = TinyDB("..\\databases\\db.json")

###

songs = {}
for song in sorted(db, key=lambda k: k["timestamp"]):
    name, timeranges = song["song"], song["timeranges"]
    if os.path.isfile(music_path+"\\"+name):
        if name not in songs:
            songs[name] = []
        for arange in timeranges:
            totallength = getlength(name)
            if totallength is not None:
                duration = (arange[1]-arange[0])/totallength
                songs[name].append(duration)

for name in songs:
    try:
        songs[name] = sum(songs[name])/len(songs[name])
    except ZeroDivisionError:
        songs[name] = 0
print("= Average number of lengths played =")
for song in sorted(songs, key=songs.get, reverse=True):
    print(round(songs[song], 2), song)

print()

songs = {}
for song in sorted(db, key=lambda k: k["timestamp"]):
    name, timeranges = song["song"], song["timeranges"]
    if os.path.isfile(music_path+"\\"+name):
        if name not in songs:
            songs[name] = 0
        for arange in timeranges:
            totallength = getlength(name)
            if totallength is not None:
                duration = (arange[1]-arange[0])/totallength
                songs[name] += duration
print("= Total number of lengths played =")
for song in sorted(songs, key=songs.get, reverse=True):
    print(round(songs[song], 2), song)

print()

###

"""
# https://www.last.fm/api/scrobbling

A track should only be scrobbled when the following conditions have been met:

* The track must be longer than 30 seconds.
* And the track has been played for at least half its duration, or for 4 minutes (whichever occurs earlier.)
"""

songs = {}
for song in sorted(db, key=lambda k: k["timestamp"]):
    name, timeranges = song["song"], song["timeranges"]
    if os.path.isfile(music_path+"\\"+name):
        totallength = getlength(name)
        if totallength is not None and totallength > 30:
            if name not in songs:
                songs[name] = [0, 0]
            totalplayed = sum([arange[1]-arange[0] for arange in timeranges])
            if ((totalplayed/totallength) >= 0.5) or (totalplayed > (60*4)):
                songs[name][0] += 1
            else:
                songs[name][1] += 1

print("= Most number of scrobbles =")
for song in sorted(songs, key=lambda k: songs[k][0], reverse=True):
    print(song, songs[song])

print()

print("= Most number of non-scrobbles =")
for song in sorted(songs, key=lambda k: songs[k][1], reverse=True):
    print(song, songs[song])

print()

print("= Highest scrobble-to-non-scrobble ratio =")
for song in sorted(songs, key=lambda k: songs[k][0]/(songs[k][0]+songs[k][1]), reverse=True):
    print(song, songs[song])
