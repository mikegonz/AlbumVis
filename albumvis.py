from __future__ import print_function
import sys
import operator
import os.path
from math import floor, ceil
import urllib.request
import colorsys
import tkinter as tk
from PIL import Image, ImageTk, ImageFilter, ImageCms

import spotipy
import spotipy.util as util
from spotipy.oauth2 import SpotifyOAuth

MAC = True

#to account for mac's retina-display messing everything up
MULT = 2 if MAC else 1

WIDTH = 2560
HEIGHT = 1600

### helper fn to return avg color sampled from top and bottom of image
def calcAverageColors(im):
    topcol = (0, 0, 0)
    botcol = (0, 0, 0)
    y = (im.height/32)
    for j in range(16):
        x = j * im.width/16 + (im.width/32)
        topcol = tuple(map(operator.add, topcol, im.getpixel((x,y))))
    
    y = 15 * im.height/16 + (im.height/32)
    for j in range(16):
        x = j * im.width/16 + (im.width/32)
        botcol = tuple(map(operator.add, botcol, im.getpixel((x,y))))
    topcol = tuple(map(operator.floordiv, topcol, (16, 16, 16)))
    botcol = tuple(map(operator.floordiv, botcol, (16, 16, 16)))
    return topcol, botcol

### render image flanked by mirrored panels on either side, with border
# on top and bottom of avg colors sampled from the top of bottom of img, respectively
# if isBlur, the mirrored side panels are blurred and muted as well
def renderImageMirrorSide(im, writePath, isBlur):
    width = floor(WIDTH / MULT)
    height = floor(HEIGHT / MULT)
    sidePanelWidth = round((width - im.width) / 2)
    borderHeight = round((height - im.height) / 2)
    topcol, botcol = calcAverageColors(im)

    leftPanel = im.crop((0, 0, sidePanelWidth, im.height)).transpose(Image.FLIP_LEFT_RIGHT)
    rightPanel = im.crop((im.width - sidePanelWidth, 0, im.width, im.height)).transpose(Image.FLIP_LEFT_RIGHT)
    
    if(isBlur):
        maskim = Image.new('RGB', (320, 640), tuple(map(operator.floordiv, tuple(map(operator.add, topcol, botcol)), (2, 2, 2))))
        leftPanel = Image.blend(leftPanel.filter(ImageFilter.GaussianBlur(10)), maskim, 0.25)
        rightPanel = Image.blend(rightPanel.filter(ImageFilter.GaussianBlur(10)), maskim, 0.25)

    fullim = Image.new('RGB', (width, height), botcol)
    fullim.paste(Image.new('RGB', (width, round(height/2)), topcol), (0, 0, width, round(height/2)))
    fullim.paste(im, (sidePanelWidth, borderHeight, sidePanelWidth + im.width, borderHeight + im.height))
    fullim.paste(leftPanel, (0, borderHeight, sidePanelWidth, im.height + borderHeight))
    fullim.paste(rightPanel, (width - sidePanelWidth, borderHeight, width, im.height + borderHeight))
    fullim.save(writePath, 'PNG')

    nextim = fullim
    return nextim

### render album art in center of a black background
def renderImageCenter(im, writePath):
    width = floor(WIDTH / MULT)
    height = floor(HEIGHT / MULT)
    fullim = Image.new('RGB', (width, height), 'black')
    fullim.paste(im, (floor(width/2 - im.width/2), floor(height/2 - im.height/2), floor(width/2 + im.width/2), floor(height/2 + im.height/2)))
    fullim.save(writePath, 'PNG')
    nextim = fullim
    return nextim        

### render album art in center of a solid ackground of a sampled average color
def renderImageSolid(im, writePath):
    width = floor(WIDTH / MULT)
    height = floor(HEIGHT / MULT)

    avgcol = (0, 0, 0)
    for i in [0,15]:
        y = i * im.height/16 + (im.height/32)
        for j in range(16):
            x = j * im.width/16 + (im.width/32)
            
            avgcol = tuple(map(operator.add, avgcol, im.getpixel((x,y))))
    for i in [1,2,3,4,5,6,7,8,9,10,11,12,13,14]:
        y = i * im.height/16 + (im.height/32)
        for j in [0,15]:
            x = j * im.width/16 + (im.width/32)
            avgcol = tuple(map(operator.add, avgcol, im.getpixel((x,y))))
            
    avgcol = tuple(map(operator.floordiv, avgcol, (60, 60, 60)))
    fullim = Image.new('RGB', (width, height), avgcol)
    fullim.paste(im, (floor(width/2 - im.width/2), floor(height/2 - im.height/2), floor(width/2 + im.width/2), floor(height/2 + im.height/2)))
    fullim.save(writePath, 'PNG')
    return fullim

### if raw album art not already in cache, fetch and save at rawpath
def fetchRawAlbumArt(track):
    albumImgUrl = track['item']['album']['images'][0]['url']
    rawpath = 'cached_albums/raw/' + track['item']['album']['id'] + '.jpg'
    if(not (os.path.isfile(rawpath))):
        urllib.request.urlretrieve(albumImgUrl, rawpath)
        imgraw = Image.open(rawpath)
        if imgraw.mode == "L": # if grayscale, convert to RGB
            imgraw = imgraw.convert("RGB")
            imgraw.save(rawpath, "PNG")
    return rawpath

### args sp, currim
### queries currently playing track and returns image of visualization, or err if no track is playing
### return err, nextim, isNew
def fetchAlbumVis(sp, currid, currim):

    track = sp.current_user_playing_track()
    if track is not None:
        if currid != track['item']['album']['id']:
            nextid = track['item']['album']['id']
            path = 'cached_albums/' + mode + '/' + nextid + '.png'
            if(os.path.isfile(path)):
                nextim = Image.open(path)
            else:
                rawpath = fetchRawAlbumArt(track)
                im = Image.open(rawpath)
                # print(rawpath, im.format, "%dx%d" % im.size, im.mode)
                if(mode == 'mirror-side'):
                    nextim = renderImageMirrorSide(im, path, False)
                elif(mode == 'mirror-side-blur'):
                    nextim = renderImageMirrorSide(im, path, True)
                elif(mode == 'center'):
                    nextim = renderImageCenter(im, path)                                    
                elif(mode == 'solid'):
                    nextim = renderImageSolid(im, path)
            return None, nextid, nextim, True
        else:
            #same track playing
            return None, currid, currim, False
    else:
        #no track playing
        return 86, None, None, None


### main fn that declares important values, defines update functions,
# and sets update loop into motion
def run(sp):
    root = tk.Tk()
    root.wm_attributes('-fullscreen','true')
    root.tk.call("::tk::unsupported::MacWindowStyle", "style", root._w, "plain", "none")

    canvas = tk.Canvas(root, width=(root.winfo_screenwidth()), height=(root.winfo_screenheight()), highlightthickness=0)
    canvas.pack()

    startim = Image.open('start.jpg')

    errim = Image.open('uhoh.jpg')
    
    canvas.image = ImageTk.PhotoImage(startim)
    canvas.create_image(0, 0, image=canvas.image, anchor='nw')

    ### loop to call fns to fetch current track, display image or call transition function accordingly
    def update(currid, currim):
        err, newid, newim, isNew = fetchAlbumVis(sp, currid, currim)
        if(err):
            canvas.image = ImageTk.PhotoImage(errim)
            canvas.create_image(0, 0, image=canvas.image, anchor='nw')
            root.after(2000, lambda : update(None, errim))
        elif(isNew):
            root.after(10, lambda : updateim(1.0, currim, newim))
            # if(changing == 0):
            #     canvas.image = ImageTk.PhotoImage(newim)
            #     canvas.create_image(0, 0, image=canvas.image, anchor='nw')
            root.after(2000, lambda : update(newid, newim))
        else:
            root.after(2000, lambda : update(currid, currim))

    ### loop to transition previm into nextim
    def updateim(changing, previm, nextim):
        if(changing > 0):
            newim = Image.blend(nextim, previm, changing)
            canvas.image = ImageTk.PhotoImage(newim)
            canvas.create_image(0, 0, image=canvas.image, anchor='nw')
            root.after(10, lambda : updateim(changing - 0.05, previm, nextim))
        elif (floor(changing*100) == 0 or ceil(changing*100) == 0):
            canvas.image = ImageTk.PhotoImage(nextim)
            canvas.create_image(0, 0, image=canvas.image, anchor='nw')

    root.after(10, lambda : update(None, startim))
    root.mainloop()
    
scope = 'user-read-currently-playing'

if len(sys.argv) > 1:
    username = sys.argv[1]
else:
    print("Usage: %s username" % (sys.argv[0],))
    sys.exit()

try:
    assert len(sys.argv) == 3
except:
    print('specify a display mode in the command line arguments, e.g. %s %s solid' % (sys.argv[0],sys.argv[1],))
    quit()
mode = sys.argv[2]
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope, username=username))
run(sp)
