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
mode = 'solid'

MULT = 2 if MAC else 1

WIDTH = 2560
HEIGHT = 1600

sp = spotipy.Spotify()

errim = Image.open('uhoh.jpg')

currid = ''
prevpath = 'uhoh.jpg'
currpath = 'uhoh.jpg'
previm = Image.open(prevpath)
nextim = Image.open(currpath)
errim = Image.open('uhoh.jpg')

changing = 0

# def is_adobe_rgb(img):
#     return 'Adobe RGB' in img.info.get('icc_profile', '')

# def adobe_to_srgb(img):
#     icc = tempfile.mkstemp(suffix='.icc')[1]
#     with open(icc, 'w') as f:
#         f.write(img.info.get('icc_profile'))
#     srgb = ImageCms.createProfile('sRGB')
#     img = ImageCms.profileToProfile(img, icc, srgb)
#     return img

def rgbtohsl(rgb):
    hls = colorsys.rgb_to_hls(rgb[0]/255, rgb[1]/255, rgb[2]/255)
    return (round(hls[0]*360), round(hls[2]*100), round(hls[1]*100))

def hsltorgb(hsl):
    rgb = colorsys.hls_to_rgb(hsl[0]/360, hsl[2]/100, hsl[1]/100)
    return (round(rgb[0]*255), round(rgb[1]*255), round(rgb[2]*255))

def rgbtohsv(rgb):
    hsv = colorsys.rgb_to_hsv(rgb[0]/255, rgb[1]/255, rgb[2]/255)
    return (round(hsv[0]*360), round(hsv[1]*100), round(hsv[2]*100))

def hsvtorgb(hsv):
    rgb = colorsys.hsv_to_rgb(hsv[0]/360, hsv[1]/100, hsv[2]/100)
    return (round(rgb[0]*255), round(rgb[1]*255), round(rgb[2]*255))

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

def renderImageMirrorSide(im, writePath, isBlur):
    width = floor(WIDTH / MULT)
    height = floor(HEIGHT / MULT)
    # print(im.width, im.height)
    
    

    sidePanelWidth = round((width - im.width) / 2)
    borderHeight = round((height - im.height) / 2)

    leftPanel = im.crop((0, 0, sidePanelWidth, im.height)).transpose(Image.FLIP_LEFT_RIGHT)
    rightPanel = im.crop((im.width - sidePanelWidth, 0, im.width, im.height)).transpose(Image.FLIP_LEFT_RIGHT)
    
    topcol, botcol = calcAverageColors(im)
    print(topcol, botcol)

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

    print("saved image to", writePath)
    nextim = fullim
    return nextim

def renderImageGradientRect(im, writePath):
    width = 2560
    height = 1600
    full = Image.new('RGB', (floor(width/MULT), floor(height/MULT)), 'black')
    try:
        full.paste(im, (floor((width/2)/MULT-320), floor((height/2)/MULT-320), floor((width/2)/MULT+320), floor((height/2)/MULT+320)))
        full.save(writePath, 'PNG')
        nextim = full
    except:
        print('image is not 640x640')
        # currpath = 'uhoh.jpg'
        nextim = errim   
    return nextim        

def renderImageSolid(im, writePath):
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
    width = 2560
    height = 1600
    full = Image.new('RGB', (floor(width/MULT), floor(height/MULT)), avgcol)
    #im = im.resize((floor(im.width/MULT), floor(im.height/MULT)))
    #full.paste(im, (floor((width/2-320)/MULT), floor((height/2-320)/MULT), floor((width/2+320)/MULT), floor((height/2+320)/MULT)))
    try:
        full.paste(im, (floor((width/2)/MULT-320), floor((height/2)/MULT-320), floor((width/2)/MULT+320), floor((height/2)/MULT+320)))
        full.save(writePath, 'PNG')
        nextim = full
    except:
        # currpath = 'uhoh.jpg'
        nextim = errim
    #full.save('full.png', 'PNG')
    return nextim

def checkalbum(sp):
    global currid
    global prevpath
    global currpath
    global changing
    global previm
    global nextim

    #print(currid)
    track = sp.current_user_playing_track()
    if track is not None:
        if currid != track['item']['album']['id']:
            print(currid)
            currid = track['item']['album']['id']
            changing = 1.0
            prevpath = currpath
            albumImgUrl = track['item']['album']['images'][0]['url']
            pathRaw = 'cached_albums/raw/' + currid + '.jpg'
            if(not (os.path.isfile(pathRaw))):
                urllib.request.urlretrieve(albumImgUrl, pathRaw)
                imgraw = Image.open(pathRaw)
                if imgraw.mode == "L":
                    imgraw = imgraw.convert("RGB")
                    imgraw.save(pathRaw, "PNG")
            currpath = path = 'cached_albums/' + mode + '/' + currid + '.png'
            if(os.path.isfile(path)):
                nextim = Image.open(path)
                # if is_adobe_rgb(nextim):
                #     nextim = adobe_to_srgb(nextim)
            else:
                im = Image.open(pathRaw)
                print(pathRaw, im.format, "%dx%d" % im.size, im.mode)
                if(mode == 'mirror-side'):
                    nextim = renderImageMirrorSide(im, path, False)
                elif(mode == 'mirror-side-blur'):
                    nextim = renderImageMirrorSide(im, path, True)
                elif(mode == 'gradient-rect'):
                    nextim = renderImageGradientRect(im, path)                                    
                elif(mode == 'solid'):
                    nextim = renderImageSolid(im, path)
            return (True, 1000)
        else:
            return (False, True)
    else:
        return (False, False)

def run(sp):
    root = tk.Tk()
 #   root.overrideredirect(True)
    root.wm_attributes('-fullscreen','true')
    root.attributes("-topmost", True)
    root.tk.call("::tk::unsupported::MacWindowStyle", "style", root._w, "plain", "none")

    canvas = tk.Canvas(root, width=(root.winfo_screenwidth()), height=(root.winfo_screenheight()), highlightthickness=0)
    canvas.pack()

    global errim
    errim = errim.resize((floor(root.winfo_screenwidth()), floor(root.winfo_screenheight())))
    
    canvas.image = ImageTk.PhotoImage(errim)
    canvas.create_image(0, 0, image=canvas.image, anchor='nw')
    def update():
        global changing
        #print(root.winfo_screenwidth(), root.winfo_screenheight())
        result = checkalbum(sp)
        if(result[0]):
            print(result[0])
            newim = Image.open(currpath)
            #newim = newim.resize((floor(root.winfo_screenwidth()), floor(root.winfo_screenheight())))
            if(changing == 0):
                canvas.image = ImageTk.PhotoImage(newim)
                canvas.create_image(0, 0, image=canvas.image, anchor='nw')
            root.after(result[1], update)
        else:
            if(not result[1]):
                canvas.image = ImageTk.PhotoImage(errim)
                canvas.create_image(0, 0, image=canvas.image, anchor='nw')
            root.after(2000, update)

    def updateim():
        global changing
        global prevpath
        global previm
        global nextim
        if(changing > 0):
            changing -= 0.05
            newim = Image.blend(nextim, previm, changing)
            canvas.image = ImageTk.PhotoImage(newim)
            canvas.create_image(0, 0, image=canvas.image, anchor='nw')
        elif (floor(changing*100) == 0 or ceil(changing*100) == 0):
            print("woo")
            newim = Image.open(currpath)
            canvas.image = ImageTk.PhotoImage(newim)
            canvas.create_image(0, 0, image=canvas.image, anchor='nw')
            changing -= 0.05
            prevpath = currpath
            previm = nextim
        root.after(10, updateim)

    root.after(10, update)
    root.after(10, updateim)
    root.after(5000, lambda: root.focus_force())
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
