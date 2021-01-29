from PIL import Image, ImageTk, ImageFilter, ImageCms
import colorsys

isMac = True

mult = 2 if isMac else 1

errim = Image.open('uhoh')


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
