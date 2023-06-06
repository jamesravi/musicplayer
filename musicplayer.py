#!/usr/bin/env python3

# Copyright (C) 2022 James Ravindran
# SPDX-License-Identifier: AGPL-3.0-or-later

import random, io, os, time, math
from pathlib import Path
import webbrowser
import base64

from flask import Flask, render_template, send_file
import mutagen
from tinydb import TinyDB
from PIL import Image

from get_music_path import get_music_path

app = Flask(__name__)
app.config["TEMPLATES_AUTO_RELOAD"] = True
basepath = get_music_path()
songscache = []
db = TinyDB(Path("databases") / "db.json")
exts = ["*.mp3", "*.opus"]

# https://stackoverflow.com/a/312464
def chunks(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]

@app.route("/")
def homepage():
    songs = []
    for filetype in exts:
        songs.extend([song.name for song in basepath.glob(filetype)])
    random.shuffle(songs)
    return render_template("musicplayer.html", songs=chunks(songs, 4))

@app.route("/getrandomsong")
def getrandomsong():
    global songscache

    if songscache == []:
        for song in sorted(db, key=lambda k: k["timestamp"]):
            song = song["song"]
            if song in songscache:
                songscache.remove(song)
            songscache.append(song)
        songscache.reverse() # So oldest played songs are more likely to be played

        allofthem = []
        for filetype in exts:
            allofthem.extend([song.name for song in basepath.glob(filetype)])
        random.shuffle(allofthem)

        # Add new unplayed songs to end of cache
        for song in allofthem:
            if song not in songscache:
                songscache.append(song)

        # Remove songs from cache if they no longer exist
        songscache[:] = [song for song in songscache if song in allofthem]

    weights = list(map(math.sqrt, range(len(songscache))))
    result = random.choices(population=songscache, weights=weights, k=1)[0]
    songscache.remove(result)      
    return result

@app.route("/getsong/<song>")
def getsong(song):
    if song in songscache:
        songscache.remove(song)
    song = basepath / song
    return send_file(song, conditional=True)

@app.route("/sendtimeranges/<song>/<timeranges>")
def sendtimeranges(song, timeranges):
    newtimeranges = []
    for timerange in timeranges.split(","):
        newtimeranges.append([float(tr) for tr in timerange.split("-")])
    db.insert({"song":song, "timeranges":newtimeranges, "timestamp":time.time()})
    return "OK"

@app.route("/getalbumart/<song>/<width>")
def getalbumart(song, width):
    width = int(width)
    song = basepath / song
    modifiedtime = os.path.getmtime(song)
    thefile = mutagen.File(song).tags
    albumart = None
    
    if type(thefile) == mutagen.oggopus.OggOpusVComment:
        assert len(thefile["metadata_block_picture"]) == 1
        try:
            albumart = mutagen.flac.Picture(base64.b64decode(thefile["metadata_block_picture"][0]))
        except (binascii.Error, mutagen.flac.error) as e:
            print("WARNING: Failed to get album art for", song)
    elif type(thefile) == mutagen.id3.ID3:
        for key in thefile.keys():
            if "APIC" in key:
                albumart = thefile[key]
                break
    else:
        # Unknown extension
        raise Exception(str(song) + " " + str(type(thefile)))
            
    if not albumart:
        raise Exception(song, thefile.keys())
    else:
        mime = albumart.mime
        albumart = albumart.data
    albumart = Image.open(io.BytesIO(albumart))
    albumart.thumbnail((width, width), Image.ANTIALIAS)
    albumartresult = io.BytesIO()
    albumart.save(albumartresult, "JPEG")
    albumartresult.seek(0)
    return send_file(albumartresult, mimetype="image/jpeg", last_modified=modifiedtime)

@app.route("/getsongname/<song>")
def getsongname(song):
    song = basepath / song
    thefile = mutagen.File(song).tags
    if type(thefile) == mutagen.oggopus.OggOpusVComment:
        songname = thefile["title"][0] + " - " + thefile["artist"][0]
    elif type(thefile) == mutagen.id3.ID3:
        songname = " ".join(thefile["TIT2"].text)
        if "TPE1" in thefile:
            songname += " - " + " ".join(thefile["TPE1"].text)
    else:
        # Unknown extension
        raise Exception(str(song) + " " + str(type(thefile)))
    return songname

app.jinja_env.globals.update(getsongname=getsongname)

webbrowser.open("http://localhost:20000")
app.run(host="127.0.0.1", port=20000)#, debug=True)
