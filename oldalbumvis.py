from __future__ import print_function
import sys
import operator
from math import floor, ceil
import os.path
import tkinter as tk
from PIL import Image, ImageTk, ImageFilter, ImageCms
import urllib.request
import spotipy
import spotipy.util as util
from spotipy.oauth2 import SpotifyClientCredentials
import colorsys

MAC = True
mode = 'solid'

mult = 1

if(MAC):
    mult = 2
    
sp = spotipy.Spotify()

errim = Image.open('uhoh.jpg')

currid = ''
prevpath = 'uhoh.jpg'
currpath = 'uhoh.jpg'
previm = Image.open(prevpath)
nextim = Image.open(currpath)
errim = Image.open('uhoh.jpg')

changing = 0

def is_adobe_rgb(img):
    return 'Adobe RGB' in img.info.get('icc_profile', '')

def adobe_to_srgb(img):
    icc = tempfile.mkstemp(suffix='.icc')[1]
    with open(icc, 'w') as f:
        f.write(img.info.get('icc_profile'))
    srgb = ImageCms.createProfile('sRGB')
    img = ImageCms.profileToProfile(img, icc, srgb)
    return img

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

print(rgbtohsl((0.5, 0.2, 0.9)))

def checkalbum(sp):
    global currid
    global prevpath
    global currpath
    global changing
    global previm
    global nextim
    result = (None, None)
    #print(currid)
    t = sp._get('me/player/currently-playing')
    if t is not None:
        if currid != t['item']['album']['id']:
            print(currid)
            currid = t['item']['album']['id']
            changing = 1.0
            prevpath = currpath
            url = t['item']['album']['images'][0]['url']
            pathRaw = 'cached_albums/raw/' + currid + '.jpg'
            if(not (os.path.isfile(pathRaw))):
                urllib.request.urlretrieve(url, pathRaw)
            #print(t['item']['album']['images'][0]['url'])
            currpath = path = 'cached_albums/' + mode + '/' + currid + '.png'
            if(os.path.isfile(path)):
                nextim = Image.open(path)
                if is_adobe_rgb(nextim):
                    nextim = adobe_to_srgb(nextim)
            elif(not (os.path.isfile(path))):
                im = Image.open(pathRaw)
                print(pathRaw, im.format, "%dx%d" % im.size, im.mode)
                if(mode == 'mirror-side'):
                    topcol = (0, 0, 0)
                    botcol = (0, 0, 0)
                    print(sp.audio_features(t['item']['id']))
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
                    width = 2560
                    height = 1600
                    maskim = Image.new('RGB', (320, 640), tuple(map(operator.floordiv, tuple(map(operator.add, topcol, botcol)), (2, 2, 2))))
                    leftim = im.crop((0, 0, 320, 640)).transpose(Image.FLIP_LEFT_RIGHT)#.filter(ImageFilter.GaussianBlur(10))
                    #leftim = Image.blend(leftim, maskim, 0.25)
                    rightim = im.crop((320, 0, 640, 640)).transpose(Image.FLIP_LEFT_RIGHT)#.filter(ImageFilter.GaussianBlur(10))
                    #rightim = Image.blend(rightim, maskim, 0.25)
                    full = Image.new('RGB', (floor(width/mult), floor(height/mult)), botcol)
                    full.paste(Image.new('RGB', (floor(width/mult), floor(height/mult/2)), topcol),
                               (0, 0, floor(width/mult), floor(height/mult/2)))
                    try:
                        full.paste(im, (floor((width/2)/mult-320), floor((height/2)/mult-320), floor((width/2)/mult+320), floor((height/2)/mult+320)))
                        full.paste(leftim, (floor((width/2)/mult-320-320), floor((height/2)/mult-320), floor((width/2)/mult-320), floor((height/2)/mult+320)))
                        full.paste(rightim, (floor((width/2)/mult+320), floor((height/2)/mult-320), floor((width/2)/mult+320+320), floor((height/2)/mult+320)))
                        full.save(path, 'PNG')
                        nextim = full
                    except:
                        print('image is not 640x640 sorry haha')
                        currpath = 'uhoh.jpg'
                        nextim = errim
                elif(mode == 'gradient-rect'):
                    print('oops')
                    width = 2560
                    height = 1600
                    full = Image.new('RGB', (floor(width/mult), floor(height/mult)), 'black')
                    try:
                        full.paste(im, (floor((width/2)/mult-320), floor((height/2)/mult-320), floor((width/2)/mult+320), floor((height/2)/mult+320)))
                        full.save(path, 'PNG')
                        nextim = full
                    except:
                        print('image is not 640x640 sorry haha')
                        currpath = 'uhoh.jpg'
                        nextim = errim                                               
                elif(mode == 'solid'):
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
                    full = Image.new('RGB', (floor(width/mult), floor(height/mult)), avgcol)
                    #im = im.resize((floor(im.width/mult), floor(im.height/mult)))
                    #full.paste(im, (floor((width/2-320)/mult), floor((height/2-320)/mult), floor((width/2+320)/mult), floor((height/2+320)/mult)))
                    try:
                        full.paste(im, (floor((width/2)/mult-320), floor((height/2)/mult-320), floor((width/2)/mult+320), floor((height/2)/mult+320)))
                        full.save(path, 'PNG')
                        nextim = full
                    except:
                        currpath = 'uhoh.jpg'
                        nextim = errim
                    #full.save('full.png', 'PNG')
                    print(avgcol)
            #return (True, t['item']['duration_ms'])
            result = (True, 1000)
            return (True, 1000)
        else:
            return (False, True)
    else:
        return (False, False)

def run(sp):
    root = tk.Tk()
    root.overrideredirect(True)
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
    

def init_spotipy(token):
    client_credentials_manager = SpotifyClientCredentials()
    sp = spotipy.Spotify(auth=token)
    util.prompt_for_user_token(username, scope, client_id='xxx', client_secret='xxx', redirect_uri='https://localhost/')
    return sp

scope = 'user-read-currently-playing'

if len(sys.argv) > 1:
    username = sys.argv[1]
else:
    print("Usage: %s username" % (sys.argv[0],))
    sys.exit()

token = util.prompt_for_user_token(username, scope)
if token:
    try:
        assert len(sys.argv) == 3
    except:
        print('specify a display mode in the command line arguments, e.g. %s %s solid' % (sys.argv[0],sys.argv[1],))
        quit()
    mode = sys.argv[2]
    sp = init_spotipy(token)
    run(sp)
else:
    print("Can't get token for " + username)
