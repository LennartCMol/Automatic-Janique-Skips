# client authentication
from cgi import test
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import spotipy.util as util

# private variable reading. user must create this file with spotify username and spotify developer client information.
import privateInfo

# random for delay and sleep
from random import randint
from time import sleep

# define scopes and authenticate client
scope = "user-read-currently-playing user-modify-playback-state user-read-playback-state playlist-read-private playlist-read-collaborative"
redirect_uri = "http://localhost:8888/callback"
token = util.prompt_for_user_token(privateInfo.userid, scope, privateInfo.CLIENT_ID, privateInfo.CLIENT_SECRET, redirect_uri)
sp = spotipy.Spotify(auth=token)

# constants
DELAY = 0.5 # delay in seconds for loop 
MINIMUM_TIME = 2 # minimum time between track skips
MAXIMUM_TIME = 5 # maximum time
PLAYLIST = "janiquevaniersel + Lennart" # get favourite tracks from Janique from blend list between Janique and Lennart 
ADDED_BY_USERID = "janiquevaniersel" # userid to check 'added by' playlist tracks

# cumstom track names that will be searched and put in favourites
track_names_to_be_searched = {
    0: "Gimme! Gimme! Gimme!",
    1: "Dancing Queen",
    2: "Lay All Your Love On Me",
    3: "New Light",
    4: "Gravity",
    5: "In the Blood",
    6: "9 to 5 ",
    7: "fdashgarhfkjdhskjfhks" # test track
}

# dictionary that will fill up with favourite tracks
favourite_track_info_list = {}

# create loop 
def loop(previous_track_uri):
    
    # get favourite tracks from custom list
    print("\nSearching for specified tracks... ")
    fillUpCustomTrackList(track_names_to_be_searched)
    print("\n\n")

    # get tracks from playlist
    playlistId = getPlaylistIdByPlaylistname(PLAYLIST, 0)
    tracksList = getAllTracksFromPlaylistAddedByUserId(playlistId, ADDED_BY_USERID)
    fillUpCustomTrackList(tracksList, False)

    print("\nAll tracks loaded. Scanning Spotify account...\n")

    while True:
        # loop delay
        sleep(DELAY)

        # check if there are any favourite tracks
        if not favourite_track_info_list:
            print("\nThere are no favourite tracks at the moment.\n")
            return
        
        if getDeviceState():
            # only check track if player is not paused
            if not getPlayingState():
                print("Track paused.\n")
                
            else:
                current_track_info = getCurrentTrackInfo()
                current_track_uri = current_track_info['track_uri']
                    
                # check if another track is playing or if track is not favourite
                if (current_track_uri != previous_track_uri or not checkIfFavourite(current_track_uri)):    
                    print("Track: " + current_track_info['track_name'] + " - " + current_track_info['artist_names'])

                    # skip if track is not a favourite track
                    if not checkIfFavourite(current_track_uri):
                            
                        # random delay between skips to mimic Janique listening to track before skipping
                        random_delay = randint(MINIMUM_TIME,MAXIMUM_TIME)
                        print("Waiting " + str(random_delay) + " seconds to skip the track to imitate Janique.\n")
                        sleep(random_delay)
                        skipCurrentTrack()
                        
                    else:
                        print("Found a track that Janique likes.\n")
                            
                # update current track
                previous_track_uri = current_track_uri    

# custom functions 

def getTrackInfo(track):
    """ Returns dictionary with track info.

    Parameters:
        - track object

    """

    album_name = track['album']['name']
    artist_names = ''
    for artists in track['artists']:
        artist_names = artist_names + artists['name'] + ', '
    artist_names = artist_names[:-2]
    track_name = track['name']
    track_uri = track['uri'].split(":")[2]
    return {
        "album_name": album_name,
        "artist_names": artist_names,
        "track_name": track_name,
        "track_uri": track_uri
    }

def getCurrentTrackInfo():
    """ Returns getTrackInfo dictionary from current track.
    """

    if(getDeviceState()):
        try:
            current_track = sp.current_user_playing_track()
            return getTrackInfo(current_track['item'])
        except:
            # catch exception
            print('\n')     

def checkIfFavourite(track_uri):
    """ Check if track is in favourites list

        Parameters:
            - track_uri
    
    """
        
    for item in favourite_track_info_list:
        if favourite_track_info_list[item]['track_uri'] == track_uri:
            return True
    return False

def getPlayingState():
    """ Return current state of playback
    """
    
    if(getDeviceState()):
        try:
            if sp.current_playback()['is_playing'] :
                return True
            else:
                return False
        except:
            # catch exception
            print('\n')

def getDeviceState():
    """ Check if any device is currently connected to Spotify
    """

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

def skipCurrentTrack():
    """ Skip currently playing track
    """

    if(getDeviceState()):
        try:
            sp.next_track()
        except:
            # catch exception
            print('\n')

def fillUpCustomTrackList(list, trackNames=True): 
    """ Update custom track list with list of tracknames provided. Can be overloaded to take tracklist with songs.

        Parameters:
            - List of tracknames OR list with tracks
            - True if tracknames, false if tracks
    """

    for key, track in list.items():
        if trackNames:
            result = searchTrack(track)
            if(result['searchState']):
                result = getTrackInfo(result['trackResult'])
                favourite_track_info_list[len(favourite_track_info_list)] = result
                printFoundTrack(result)
        else:
            result = track
            favourite_track_info_list[len(favourite_track_info_list)] = result
            printFoundTrack(result)

def getPlaylistIdByPlaylistname(playlistName, offsetIndex=0):
    """ Search provided playlist in user's playlists

        Parameters:
            - Name of the playlist
            - Offset for recursive use. Default = 0.
    """
    
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

def searchTrack(trackName):
    """ Search track by name with Spotify's search algoritmh. 
        Returns dictionary with search state and search result.

        Parameters:
            - Track name in text
    """

    print("\n\tSearching for: '" + trackName + "'...")
    try:
        track = sp.search(q='track:' + trackName, type='track', limit = 1)['tracks']['items'][0]
        return {
            "searchState": True,
            "trackResult": track 
            }
    except:
        print("\n\tTrack not found: '" + trackName + "'")
        return {
            "searchState": False,
            "trackResult": None 
            }

def getAllTracksFromPlaylistAddedByUserId(playlistId, userid):
    """ Get all tracks from a playlist added by a certain userid

        Parameters:
            - Provide playlist id
            - Provide userid to select tracks from
    """
    
    tracks = sp.playlist(playlistId)['tracks']['items']
    tracksDict = {}
    for track in tracks:
        added_by = track['added_by']['id']
        if added_by == userid:
            trackinfo = getTrackInfo(track['track'])
            tracksDict[len(tracksDict)] = trackinfo
            printFoundTrack(trackinfo)
    return tracksDict
        
def printFoundTrack(trackInfo):
    """ Print track info: track name, artist(s), album and uri.
    """
    print("\n\tFound: '" + trackInfo['track_name'] + "' by '" + trackInfo['artist_names'] + "' from album '" + trackInfo['album_name'] + "' with uri '" + trackInfo['track_uri'] + "'")


loop("no track yet")