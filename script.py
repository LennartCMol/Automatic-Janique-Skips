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
PLAYLIST = "janiquevaniersel + Lennart" # get favourite songs from Janique from blend list between Janique and Lennart 

# add to favourite songs list 
favourite_song_name_list = {
    0: "Gimme! Gimme! Gimme!",
    1: "Dancing Queen",
    2: "Lay All Your Love On Me",
    3: "New Light",
    4: "Gravity",
    5: "In the Blood",
    6: "9 to 5 "
}

# will fill up with favourite songs
favourite_song_info_list = {}

# loop that checks track on timer call
from random import randint
from time import sleep

# create loop that updates every second
def loop(previous_track_uri):
    
    # get favourite songs 
    print("\nSearching for specified songs... ")
    # from songslist
    fillUpCustomSongList(favourite_song_name_list)
    print("\n\n")

    # from playlist
    playlistId = getPlaylistIdByPlaylistname(PLAYLIST, 0)
    songsList = getSongsFromPlaylist(playlistId, privateInfo.userid)
    fillUpCustomSongList(songsList, True)
    print("\nAll songs loaded. Scanning Spotify account...\n")

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
                current_track_info = getCurrentTrackInfo()
                current_track_uri = current_track_info['song_uri']
                    
                # check if another track is playing or if track is not favourite
                if (current_track_uri != previous_track_uri or not checkIfFavourite(current_track_uri)):    
                    print("Track: " + current_track_info['song_name'] + " - " + current_track_info['artist_names'])

                    # skip if track is not a favourite track
                    if not checkIfFavourite(current_track_uri):
                            
                        # random delay between skips to mimic Janique listening to track before skipping
                        random_delay = randint(MINIMUM_TIME,MAXIMUM_TIME)
                        print("Waiting " + str(random_delay) + " seconds to skip the track to imitate Janique.\n")
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
def getCurrentTrackInfo():
    """ Returns getSongInfo dictionary from current song.
    """

    if(getDeviceState()):
        current_track = sp.current_user_playing_track()
        return getSongInfo(current_track['item'])

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
def fillUpCustomSongList(list, trackKnown=False): 
    for key, song in list.items():
        if trackKnown:
            result = song
        else:
            result = getSongInfoBySongname(song)
        songIndex = len(favourite_song_info_list)
        favourite_song_info_list[songIndex] = result
        printFoundSong(result)

# search for specified playlist within user's playlists
def getPlaylistIdByPlaylistname(playlistName, offsetIndex):
    playlists = sp.current_user_playlists(offset=offsetIndex)
    available_playlists = len(playlists['items'])
    playlistId = ""
    for playlist in playlists['items']:
        if playlist['name'] == playlistName:
            playlistId = playlist['id']
    if playlistId == "" and available_playlists == 0:
        print("\nSpecified playlist does not exist.\n")
        return
    elif playlistId == "":
        offsetIndex = offsetIndex + available_playlists
        playlistId = getPlaylistIdByPlaylistname(playlistName, offsetIndex)
    else:
        return playlistId

# return songinfo 
# can be overloaded with trackKnown. if not provided will search by songname
def getSongInfoBySongname(songName, trackKnown=False):
    if not trackKnown:
        # will search track with api search function
        print("\n\tSearching for: '" + songName + "'...")
        song = sp.search(q='track:' + songName, type='track', limit = 1)['tracks']['items'][0]
    else:
        # track is already known and has all information
        song = songName

    songInfo = getSongInfo(song)
    return songInfo
    

# returns dictionary with song info
def getSongInfo(song):
    album_name = song['album']['name']
    artist_names = ''
    for artists in song['artists']:
        artist_names = artist_names + artists['name'] + ', '
    artist_names = artist_names[:-2]
    song_name = song['name']
    song_uri = song['uri'].split(":")[2]
    return {
        "album_name": album_name,
        "artist_names": artist_names,
        "song_name": song_name,
        "song_uri": song_uri
    }

# get songs from playlist and put them in favourite songs.
# can be overloaded with userid
def getSongsFromPlaylist(playlistId, userid=None):
    songs = sp.playlist(playlistId)['tracks']['items']
    songsDict = {}
    for song in songs:
        if userid is not None:
            added_by = song['added_by']['id']
            if not added_by == userid:
                songinfo = getSongInfoBySongname(song['track'], True)
                songsDict[len(songsDict)] = songinfo
                printFoundSong(songinfo)
        else:
            songinfo = getSongInfoBySongname(song['track'], True)
            songsDict[len(songsDict)] = songinfo
            printFoundSong(songinfo)
    return songsDict
        
def printFoundSong(songInfo):
    print("\n\tFound: '" + songInfo['song_name'] + "' by '" + songInfo['artist_names'] + "' from album '" + songInfo['album_name'] + "' with uri '" + songInfo['song_uri'] + "'")


loop("no track yet")