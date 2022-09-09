# client authentication
from cgi import test
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import spotipy.util as util

# private variable reading. user must create this file with spotify username and spotify developer client information.
import privateInfo

# set up authentication for Spotify device and define scopes
scope = "user-read-currently-playing user-modify-playback-state user-read-playback-state playlist-read-private playlist-read-collaborative"
redirect_uri = "http://localhost:8888/callback"

# authentication token and create client with said token
token = util.prompt_for_user_token(privateInfo.userid, scope, privateInfo.CLIENT_ID, privateInfo.CLIENT_SECRET, redirect_uri)
sp = spotipy.Spotify(auth=token)

# constants
DELAY = 0.5 # delay in seconds for loop 
MINIMUM_TIME = 2 # minimum time between track skips
MAXIMUM_TIME = 5 # maximum time
#PLAYLIST = "janiquevaniersel + Lennart"
PLAYLIST = "Eminem"

# search for specified playlist within user's playlists
def getPlaylistIdByPlaylistname(playlistName, offsetIndex):
    playlists = sp.current_user_playlists(offset=offsetIndex)
    available_playlists = len(playlists['items'])
    playlistId = ""
    for playlist in playlists['items']:
        if playlist['name'] == playlistName:
            playlistId = playlist['id']
    if playlistId == "" and available_playlists == 0:
        print("Specified playlist does not exist.\n")
        return
    elif playlistId == "":
        offsetIndex = offsetIndex + available_playlists
        playlistId = getPlaylistIdByPlaylistname(playlistName, offsetIndex)
    else:
        return playlistId

# search for specified song name
def getSongInfoBySongname(songName):
    if(getDeviceState()):
        result = sp.search(q='track:' + songName, type='track', limit = 1)['tracks']['items'][0]
        album_name = result['album']['name']
        artist_names = ''
        for artists in result['artists']:
            artist_names = artist_names + artists['name'] + ', '
        artist_names = artist_names[:-2]
        song_name = result['name']
        song_uri = result['uri'].split(":")[2]
        return {
            "album_name": album_name,
            "artist_names": artist_names,
            "song_name": song_name,
            "song_uri": song_uri
        }

# add to favourite songs list 
favourite_song_name_list = [
    "Gimme! Gimme! Gimme!",
    "Dancing Queen",
    "Lay All Your Love On Me",
    "New Light",
    "Gravity",
    "In the Blood"
]

# will fill up with songs
favourite_song_info_list = {}

# loop that checks track on timer call
from random import randint
from time import sleep


# create loop that updates every second
def loop(previous_track_uri):

    # get favourite songs 
    fillUpSongCustomSongList()

    while True:
        # update loop every half a second
        sleep(DELAY)

        # check if there are any favourite songs
        if not favourite_song_info_list:
            print("\nThere are no favourite songs at the moment.\n")
            return
        
        if getDeviceState():
            # only check track if player is not paused
            if not getPlayingState():
                print("Track paused.\n")
                
            else:
                current_track_uri = getTrackUri()
                    
                # check if another track is playing or if track is not favourite
                if (current_track_uri != previous_track_uri or not checkIfFavourite(current_track_uri)):    
                    print(getTrackInfo())    

                    # skip if track is not a favourite track
                    if not checkIfFavourite(current_track_uri):
                            
                        # random delay between skips to mimic Janique listening to track before skipping
                        random_delay = randint(MINIMUM_TIME,MAXIMUM_TIME)
                        print("Waiting " + str(random_delay) + " seconds to skip the track.\n")
                        sleep(random_delay)
                        try:
                            sp.next_track()
                        except:
                            # catch exception
                            print('\n')
                    else:
                        print("Found a track that Janique likes.\n")
                            
                            
                # update current track
                previous_track_uri = current_track_uri    
        


# custom functions 

# get track artist and name
def getTrackInfo():
    if(getDeviceState()):
        track_info = sp.current_user_playing_track()
        track_name = track_info['item']['name']
        artist_names = ''
        for artists in track_info['item']['artists']:
            artist_names = artist_names + artists['name'] + ', '
        artist_names = artist_names[:-2]
        return "Track: " + track_name + " by " + artist_names + "."

# get track uri
def getTrackUri():
    if(getDeviceState()):
        track_info = sp.current_user_playing_track()
        track = track_info['item']['uri']
        return track.split(":")[2]

# check if uri matches an uri in the list 
def checkIfFavourite(track_uri):
    if(getDeviceState()):
        boolVar = False
        for item in favourite_song_info_list:
            if favourite_song_info_list[item]['song_uri'] == track_uri:
                boolVar = True
        if boolVar:
            return True
        else: 
            return False

# get playing state
def getPlayingState():
    if(getDeviceState()):
        if sp.current_playback()['is_playing'] :
            return True
        else:
            return False

#get device state
def getDeviceState():
    try:
        if sp.devices()['devices']:
            if sp.devices()['devices'][0]['is_active']:
                return True
            else:
                print("No active devices. \n")
                return False 
        else:
            print("No active devices. \n")
            return False
    except:
        # catch exception
        print('\n')

# fill up song_info_list
def fillUpSongCustomSongList(): 
    print("\nSearching for specified songs... ")
    songItem = 0
    for song in favourite_song_name_list:
        songItem = songItem + 1
        print("\n\tSearching for: '" + song + "'...")
        result = getSongInfoBySongname(song)
        favourite_song_info_list[songItem] = result
        print("\tFound: '" + favourite_song_info_list[songItem]['song_name'] + "' by '" + favourite_song_info_list[songItem]['artist_names'] + "' from album '" + favourite_song_info_list[songItem]['album_name'] + "' with uri '" + favourite_song_info_list[songItem]['song_uri'] + "'")
    print("\nAll songs loaded. Scanning Spotify account...\n")


test = getPlaylistIdByPlaylistname(PLAYLIST, 0)
test = 1
loop("no track yet")