import soundcloud
import urllib
import os
import sys
from subprocess import call
from pydub import AudioSegment
from random import randrange

client = soundcloud.Client(client_id='cdbefc208d1db7a07c5af0e27e10b403')

while True:
    tracks = client.get('/tracks', q='downloadable', limit=50, offset=randrange(0,8001))

    for track in tracks:
        # if track is smaller than 10M and has a download URL
        if track.original_content_size < 10000000 and hasattr(track, 'download_url'):
            # download the track
            f = track.title + '.' + track.original_format
            urllib.urlretrieve(track.download_url + '?client_id=cdbefc208d1db7a07c5af0e27e10b403', f)
            
            # create a random 5 second clip
            audio = AudioSegment.from_file(f, os.path.splitext(f)[1][1:])
            os.remove(f)
            start = randrange(0,int(audio.duration_seconds) - 4) * 1000
            slicedAudio = audio[start:start + 5000]
            clip = os.path.splitext(f)[0] + '.mp3'
            slicedAudio.export(clip, format="mp3")

            # play the clip
            print "\nThis clip provided by push-roulette and brought to you by SoundCloud"
            print "\tTitle: " + track.title
            print "\tArtist: " + track.user['username']
            print "\tGenre: " + track.genre + "\n"
            call(["afplay", clip])
            os.remove(clip)
            sys.exit()
