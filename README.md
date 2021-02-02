# AlbumVis - Spotify Album Art Visualizer

## What is this?

AlbumVis is a fullscreen application that displays the album artwork of a Spotify user’s currently playing track. The username and the display mode are passed in as command line arguments when the application is started.

## How do I run this?

Currently, this application can only be run by the owner of a Spotify developer application ID and secret ID, to authorize queries to a user’s currently playing track. If this ever grows to more than a pet project this should no longer be the case.

If you do have a client ID and secret, or you are me—directions giving the _spotipy_ library access to the proper credentials and for running this application are found in the file `runexample.sh`.

If spotify credentials have been exported as environment variables, run like so:

`python3 albumvis.py <username> <display_mode>`

### display modes - example images are in top-level directory named example\*.png

- **center** - display album image on a black background
- **solid** - display image on a background of an appropriate color
- **mirror-side** - display image side by side with mirrored images
- **mirror-side-blur** - same as above but with the mirrored images blurred and blended

## Internals

The application’s update loop queries the Spotify API every 2 seconds for the user’s currently playing track. If the track has changed since the last update, it checks if a track from this album has been played before. If so, it can grab the album artwork image from its directory of cached images. Otherwise, it gets the album artwork URL from the API call’s response and saves it to the cache.

If AlbumVis has seen this song before while running under the same visualization mode, then it can grab the rendered fullscreen visualization from the cache and display that. If not, it calls the appropriate render function to create this visualization—perhaps by placing the album artwork on a background of an appropriate color, or creating a mirror effect with several copies of the image. The visualization for the previous track fades into the new one and waits for the next update.

## Future

In the future I’d like to make this project be more distributable, with a backend interacting with the Spotify API directly and a simple graphic client—but for now it’s just a pet project.
