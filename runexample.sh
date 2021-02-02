#!/bin/bash
export SPOTIPY_CLIENT_ID=''
export SPOTIPY_CLIENT_SECRET=''
export SPOTIPY_REDIRECT_URI=''
python3 albumvis.py <username> <display-mode>
# display mode is one of:
#   solid
#   center
#   mirror-side
#   mirror-side-blur
