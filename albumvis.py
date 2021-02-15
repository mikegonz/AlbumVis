from __future__ import print_function
import sys
import operator
import os.path
from math import floor, ceil
import urllib.request
import tkinter as tk
from PIL import Image, ImageTk, ImageFilter, ImageCms
import spotipy
from spotipy.oauth2 import SpotifyOAuth

MAC = True

#to account for mac's retina-display messing everything up
MULT = 2 if MAC else 1

WIDTH = 2560
HEIGHT = 1600

### helper fn to return avg color sampled from top and bottom of image
def calculate_average_colors(im, sample_count):
    top_color = (0, 0, 0)
    bottom_color = (0, 0, 0)
    y = (im.height/(sample_count*2))
    for j in range(sample_count):
        x = j * im.width/sample_count + (im.width/(sample_count*2))
        top_color = tuple(map(operator.add, top_color, im.getpixel((x,y))))
    
    y = 15 * im.height/sample_count + (im.height/(sample_count*2))
    for j in range(sample_count):
        x = j * im.width/sample_count + (im.width/(sample_count*2))
        bottom_color = tuple(map(operator.add, bottom_color, im.getpixel((x,y))))
    top_color = tuple(map(operator.floordiv, top_color, (sample_count, sample_count, sample_count)))
    bottom_color = tuple(map(operator.floordiv, bottom_color, (sample_count, sample_count, sample_count)))
    return top_color, bottom_color

### render image flanked by mirrored panels on either side, with border
# on top and bottom of avg colors sampled from the top of bottom of img, respectively
# if is_blur, the mirrored side panels are blurred and muted as well
def render_image_mirror_side(im, write_path, is_blur):
    COLOR_SAMPLE_COUNT = 16
    BLUR_FACTOR = 10
    BLEND_FACTOR = 0.25

    width = floor(WIDTH / MULT)
    height = floor(HEIGHT / MULT)
    side_panel_width = round((width - im.width) / 2)
    border_height = round((height - im.height) / 2)
    top_color, bottom_color = calculate_average_colors(im, COLOR_SAMPLE_COUNT)

    left_panel = im\
        .crop((0, 0, side_panel_width, im.height))\
        .transpose(Image.FLIP_LEFT_RIGHT)
    right_panel = im\
        .crop((im.width - side_panel_width, 0, im.width, im.height))\
        .transpose(Image.FLIP_LEFT_RIGHT)

    if(is_blur):
        maskim = Image.new('RGB', (side_panel_width, im.height), tuple(map(operator.floordiv, tuple(map(operator.add, top_color, bottom_color)), (2, 2, 2))))
        left_panel = Image.blend(
            left_panel.filter(ImageFilter.GaussianBlur(BLUR_FACTOR)),
            maskim, BLEND_FACTOR)
        right_panel = Image.blend(
            right_panel.filter(ImageFilter.GaussianBlur(BLUR_FACTOR)),
            maskim, BLEND_FACTOR)

    fullim = Image.new('RGB', (width, height), bottom_color)
    fullim.paste(Image.new('RGB', (width, round(height/2)), top_color), (0, 0, width, round(height/2)))
    fullim.paste(im, (side_panel_width, border_height, side_panel_width + im.width, border_height + im.height))
    fullim.paste(left_panel, (0, border_height, side_panel_width, im.height + border_height))
    fullim.paste(right_panel, (width - side_panel_width, border_height, width, im.height + border_height))
    fullim.save(write_path, 'PNG')
    return fullim

### render album art in center of a black background
def render_image_center(im, write_path):
    width = floor(WIDTH / MULT)
    height = floor(HEIGHT / MULT)
    fullim = Image.new('RGB', (width, height), 'black')
    fullim.paste(im, (floor(width/2 - im.width/2), floor(height/2 - im.height/2), floor(width/2 + im.width/2), floor(height/2 + im.height/2)))
    fullim.save(write_path, 'PNG')
    return fullim        

### render album art in center of a solid background of a sampled average color
def render_image_solid(im, write_path):
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
    fullim.save(write_path, 'PNG')
    return fullim

### if raw album art not already in cache, fetch and save at rawpath
def fetch_raw_album_art(track):
    album_img_url = track['item']['album']['images'][0]['url']
    rawpath = 'cached_albums/raw/' + track['item']['album']['id'] + '.jpg'
    if(not (os.path.isfile(rawpath))):
        urllib.request.urlretrieve(album_img_url, rawpath)
        imgraw = Image.open(rawpath)
        if imgraw.mode == "L": # if grayscale, convert to RGB
            imgraw = imgraw.convert("RGB")
            imgraw.save(rawpath, "PNG")
    return rawpath

### args sp, currim
### queries currently playing track and returns image of visualization, or err if no track is playing
### return err, nextim, isNew
def get_album_visualization(sp, currid, currim):

    track = sp.current_user_playing_track()
    if track is not None:
        if currid != track['item']['album']['id']:
            nextid = track['item']['album']['id']
            path = 'cached_albums/' + mode + '/' + nextid + '.png'
            if(os.path.isfile(path)):
                nextim = Image.open(path)
            else:
                rawpath = fetch_raw_album_art(track)
                im = Image.open(rawpath)
                # print(rawpath, im.format, "%dx%d" % im.size, im.mode)
                if(mode == 'mirror-side'):
                    nextim = render_image_mirror_side(im, path, False)
                elif(mode == 'mirror-side-blur'):
                    nextim = render_image_mirror_side(im, path, True)
                elif(mode == 'center'):
                    nextim = render_image_center(im, path)                                    
                elif(mode == 'solid'):
                    nextim = render_image_solid(im, path)
            return None, nextid, nextim, True
        else:
            #same track playing
            return None, currid, currim, False
    else:
        #no track playing
        return 86, None, None, None


### main fn that declares important values, defines update functions,
# and sets update loop in motion
# arg sp is initialized Spotipy object
def run(sp):
    UPDATE_INTERVAL = 2000
    FADE_INTERVAL = 10
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
        err, newid, newim, isNew = get_album_visualization(sp, currid, currim)
        if(err):
            canvas.image = ImageTk.PhotoImage(errim)
            canvas.create_image(0, 0, image=canvas.image, anchor='nw')
            root.after(UPDATE_INTERVAL, lambda : update(None, errim))
        elif(isNew):
            root.after(10, lambda : fade_to_next_image(1.0, currim, newim))
            root.after(UPDATE_INTERVAL, lambda : update(newid, newim))
        else:
            root.after(UPDATE_INTERVAL, lambda : update(currid, currim))

    ### loop to transition previm into nextim
    def fade_to_next_image(fade_val, previm, nextim):
        if(fade_val > 0):
            newim = Image.blend(nextim, previm, fade_val)
            canvas.image = ImageTk.PhotoImage(newim)
            canvas.create_image(0, 0, image=canvas.image, anchor='nw')
            root.after(FADE_INTERVAL, lambda : fade_to_next_image(fade_val - 0.05, previm, nextim))
        else:
            canvas.image = ImageTk.PhotoImage(nextim)
            canvas.create_image(0, 0, image=canvas.image, anchor='nw')

    root.after(FADE_INTERVAL, lambda : update(None, startim))
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
