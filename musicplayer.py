#!/usr/bin/env python3

# Copyright (C) 2022 James Ravindran
# SPDX-License-Identifier: AGPL-3.0-or-later

from flask import Flask, render_template, send_file
from mutagen import File
import random, io, os, time
from tinydb import TinyDB
from PIL import Image
import webbrowser
from get_music_path import get_music_path
from pathlib import Path

app = Flask(__name__)
basepath = get_music_path()
songscache = [song.name for song in basepath.glob("*.mp3")]
random.shuffle(songscache)
db = TinyDB(Path("databases") / "db.json")

# https://stackoverflow.com/a/312464
def chunks(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]

@app.route("/")
def homepage():
    for song in basepath.glob("*.mp3"):
        newsong = " ".join(str(song).split())
        if song != newsong:
            os.rename(song, newsong)
    songs = [song.name for song in basepath.glob("*.mp3")]
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

        allofthem = list(basepath.glob("*.mp3"))
        random.shuffle(allofthem)

        for song in allofthem:
            if song.name not in songscache:
                songscache.append(song.name)
        songscache.reverse()

    result = random.choices(population=songscache, weights=range(len(songscache)), k=1)[0]
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
    thefile = File(song).tags
    albumart = None
    for key in thefile.keys():
        if "APIC" in key:
            albumart = File(song).tags[key].data
            break
    if not albumart:
        raise Exception(thefile.keys())
    albumart = Image.open(io.BytesIO(albumart))
    albumart.thumbnail((width, width), Image.ANTIALIAS)
    albumartresult = io.BytesIO()
    albumart.save(albumartresult, "JPEG")
    albumartresult.seek(0)
    return send_file(albumartresult, mimetype="image/jpeg", last_modified=modifiedtime)

@app.route("/loading.gif")
def loading():
    return send_file("loading.gif")

webbrowser.open("http://localhost:20000")
app.run(host="127.0.0.1", port=20000)#, debug=True)
