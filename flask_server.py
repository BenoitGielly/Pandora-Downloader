"""Download songs from Pandora using a Flask server.

:created:
:author:

"""
from __future__ import print_function

import os
import re
import urllib

from flask import Flask, jsonify, request
from mutagen.mp4 import MP4, MP4Cover

# =============================================================================
# config
# =============================================================================
# modify These lines to change where the songs are saved
ROOT_FOLDER = r"D:\musics\Pandora"

# possible Variables - Mix and match as desired
# {station} {artist} {album} {title}
FILE_TEMPLATE = os.sep.join(
    (
        "{station}",
        "{artist}",
        "{title}.m4a",
        # "{album} - {title}.m4a"
    )
)

# =============================================================================
APP = Flask("Pandora Downloader Server")


@APP.route("/download", methods=["POST"])
def pandora_downloader():
    """Download songs from Pandora, Woop Woop."""
    # playlist path
    playlist_path = os.sep.join(
        [
            ROOT_FOLDER,
            re.sub(r'[<>\*:\\/"|?]', "", request.form["station"]) + ".m3u",
        ]
    )

    # build the song's path - remove any invalid characters
    relative_song_path = FILE_TEMPLATE.format(
        station=re.sub(r'[<>\*:\\/"|?]', "", request.form["station"]),
        artist=re.sub(r'[<>\*:\\/"|?]', "", request.form["artist"]),
        album=re.sub(r'[<>\*:\\/"|?]', "", request.form["album"]),
        title=re.sub(r'[<>\*:\\/"|?]', "", request.form["title"]),
    )

    song_path = os.sep.join([ROOT_FOLDER, relative_song_path])

    # check to see if the file has been downloaded before!
    if os.path.exists(song_path):
        print("Song found already")
        return jsonify(status="alreadyDownloaded")
    else:
        print("Downloading {!r}".format(request.form["title"]))

        # create the directories if they don't exist
        if not os.path.isdir(os.path.split(song_path)[0]):
            os.makedirs(os.path.split(song_path)[0])

        # download the song
        try:
            urllib.urlretrieve(request.form["url"], song_path)
        except BaseException:
            print("Something went wrong... skipping this song!")
            return jsonify(status="failed")

        # open the song with mutagen so we can tag it
        # and put the album art in it
        try:
            song = MP4(song_path)
        except BaseException:
            print("Something went wrong... skipping this song!")
            return jsonify(status="failed")

        # set the tags
        song["\xa9nam"] = [request.form["title"]]
        song["\xa9ART"] = [request.form["artist"]]
        song["\xa9alb"] = [request.form["album"]]

        # download the album art and put it in the file
        album_art_request = urllib.urlopen(request.form["albumArt"])
        album_art = MP4Cover(album_art_request.read())
        album_art_request.close()
        song["covr"] = [album_art]
        song.save()

        # append the song in the playlist
        with open(playlist_path, "a+") as playlist:
            playlist.write((relative_song_path + "\n"))

        print("Download Complete!")
        return jsonify(status="success")


if __name__ == "__main__":
    APP.run(debug=True)
