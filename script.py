# client authentication
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import spotipy.util as util

# private variable reading. user must create this file with spotify username and spotify developer client information.
import privateInfo

# set up authentication for Spotify device and define scopes
scope = "user-read-currently-playing user-modify-playback-state user-read-playback-state"
redirect_uri = "http://localhost:8888/callback"

# authentication token and create client with said token
token = util.prompt_for_user_token(privateInfo.username, scope, privateInfo.CLIENT_ID, privateInfo.CLIENT_SECRET, redirect_uri)
sp = spotipy.Spotify(auth=token)



# uri IDs of songs that Janique likes (test songs for now)
uri_list = [
    "3vkQ5DAB1qQMYO4Mr9zJN6", # Gimme! Gimme! Gimme - ABBA
    "0GjEhVFGZW8afUYGChu3Rr", # Dancing Queen - ABBA
    "2245x0g1ft0HC7sf79zbYN", # Lay All Your Love On Me - ABBA
    "4T6FWA703h6H7zk1FoSARw", # New Light - John Mayer
    "3SktMqZmo3M9zbB7oKMIF7", # Gravity - John Mayer
    "77Y57qRJBvkGCUw9qs0qMg"  # In the Blood - John Mayer
]

# constants
DELAY = 0.5 # delay in seconds for loop 
MINIMUM_TIME = 2 # minimum time between track skips
MAXIMUM_TIME = 5 # maximum time


# loop that checks track on timer call
from random import randint
from time import sleep

# create loop that updates every second
def loop(previous_track_uri):
    
    while True:
        # update loop every half a second
        sleep(DELAY)

        if getDeviceState():
            # only check track if player is not paused
            if not getPlayingState():
                print("Track paused.")
                
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
        if track_uri in uri_list:
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

loop("no track yet")