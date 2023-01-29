// Copyright (C) 2022 James Ravindran
// SPDX-License-Identifier: AGPL-3.0-or-later

function httpGetAsync(theUrl, callback) {
	var xmlHttp = new XMLHttpRequest();
	xmlHttp.onreadystatechange = function() { 
		if (xmlHttp.readyState == 4 && xmlHttp.status == 200) {
			callback(xmlHttp.responseText);
		}
	}
	xmlHttp.open("GET", theUrl, true);
	xmlHttp.send(null);
}

function getTimeRanges() {
	var timeranges = audio.played;
	var result = [];
	for (var i = 0; i < timeranges.length; i++) {
		result.push(timeranges.start(i)+"-"+timeranges.end(i));
	}
	return result.join();
}

function _loadSong(song) {
	song = song.trim();
	source.src = "getsong/" + song;
	httpGetAsync("getsongname/" + song, function(res) {
		document.getElementById("currentsong").textContent = res;
	});
	audio.load();
	audio.play();
}

function sendTimeRanges(callback) {
	httpGetAsync("/sendtimeranges/" + source.src.split("/")[source.src.split("/").length - 1] + "/" + getTimeRanges(), callback);
}

function loadSong(song) {
	if (playedyet && document.getElementById("sendplayedranges").checked) {
		sendTimeRanges(function(res) {
			_loadSong(song)
		});
	} else {
		_loadSong(song)
		playedyet = true;
	}
}

function loadRandomSong() {
	httpGetAsync("/getrandomsong", function(res) {
		loadSong(res);
	});
}

function processSong(e) {
	loadSong(e.dataset.song);
}

window.onload = function() {
	audio = document.getElementsByTagName("audio")[0];
	source = document.getElementsByTagName("source")[0];
	audio.onended = function() {
		loadRandomSong();
	}
	//loadRandomSong();
	Array.from(document.getElementsByClassName("cell")).forEach(function(e) {
		e.getElementsByTagName("img")[0].src = "/getalbumart/" + e.dataset.song + "/" + window.innerWidth/4
	});
	
	//Array.from(document.getElementsByTagName("img"))
	playedyet = false;
}

window.onbeforeunload = function (e) {
	if (playedyet && document.getElementById("sendplayedranges").checked) {
		sendTimeRanges(null);
	}
}
