#!/usr/bin/env python3

#-------------------------------------#

### import ###

import sys
import os
import time
import subprocess
import json
import signal
import random
import math

from PIL import Image, ImageDraw, ImageFont
import twitter

#-------------------------------------#

### Parameters ###

is_debug_mode: bool = False

with open('config.json', 'r') as f:
    prm: dict = json.load(f)

twitter_credentials_file: str = './twitter_credentials.json'

output_image_file: str = os.path.expanduser(prm['output_image_file'])

num_trial: int = 3 #the number of times we try to send a request (since it may fail due to timeout)

interval_sec: int = 60

timeout_sec: int = 30

header_size: tuple = (1500, 500) #This is the officially recommended size. ref: |https://help.twitter.com/en/managing-your-account/common-issues-when-uploading-profile-photo|

font_name: str = prm['font_name']
font_size: int = 35

color_mode: str = 'RGB'
bg_color: int = (0x3C, 0x3C, 0x3C)
fg_color: int = (0xDD, 0xDD, 0xDD)

should_draw_sun_or_moon: bool = prm['should_draw_sun_or_moon']
sun_radius: int = 40
sun_color: int = (0xEF, 0x8E, 0x38)
moon_color: int = (0xFE, 0xFA, 0xD4)

#-------------------------------------#

### Signal Handlers ###

def signal_handler(signal, frame) -> None:
    print()
    print(f'(main.py) Signal {signal} was caught.')
    sys.exit(1)

signal.signal(signal.SIGTERM, signal_handler)
signal.signal(signal.SIGINT, signal_handler)

#-------------------------------------#

### Classes ###

class Twitter:

    def __init__(self, twitter_credentials_file: str):

        print('Twitter: Logging in...')

        with open(twitter_credentials_file, 'r') as f_in:
            twitter_credentials: dict = json.load(f_in)

        self.twitter_client: object = twitter.Api(
                                                   consumer_key        = twitter_credentials['api_key'],
                                                   consumer_secret     = twitter_credentials['api_secret_key'],
                                                   access_token_key    = twitter_credentials['access_token'],
                                                   access_token_secret = twitter_credentials['access_token_secret'],
                                                   timeout             = timeout_sec
                                                 )

        print('Twitter: Logged in.')

    def change_header_image_(self, image_path: str) -> None:
        print('-----')
        for i in range(num_trial):
            try:
                if (i != 0):
                    print()
                print(f'[{i}/{num_trial}] Uploading the header image...')
                self.twitter_client.UpdateBanner(image_path)
                print('Done.')
                break
            except:
                pass

#-------------------------------------#

### Functions ###

def create_date_string() -> str:

    date_string: str = time.strftime('%Y/%m/%d(%a)%H:%M %Z(%z)')

    cow_command: tuple = ('cowsay', 'cowthink')
    cow_type: tuple = ('www', 'udder', 'small', 'moose', 'default')
    cow_expression: tuple = (None, '-b', '-d', '-g', '-p', '-s', '-t', '-w', '-y')

    command: list = [random.choice(cow_command), '-f', random.choice(cow_type)]
    if (tmp := random.choice(cow_expression)):
        command.append(tmp)
    command.append(date_string)

    return subprocess.run(command, capture_output = True).stdout.decode('utf-8')

#experimental
def draw_sun_or_moon(draw_object: ImageDraw.Draw) -> None:

    #The orbit of the Sun and the Moon is on this circle.
    #This circle is generally larger then the size of the header image and its center is below the header image.
    x: float = header_size[0] / 2
    y: float = header_size[1] * 2
    r: float = y * 1.015

    #the angles of sunrise and sunset
    max_radian: float = 2.46
    min_radian: float = 0.69
    delta_radian: float = (max_radian - min_radian) / (12 * 60)

    night_start_hour: int = 18
    night_end_hour: int = 6

    current_time: object = time.localtime()

    if (night_end_hour <= current_time.tm_hour < night_start_hour): #sun
        theta: float = max_radian - ((current_time.tm_hour - night_end_hour) * 60 + current_time.tm_min) * delta_radian
        X: int = int(x + r * math.cos(theta)) #`X` and `Y` define the bounding box of the Sun or the Moon.
        Y: int = int(y - r * math.sin(theta))
        draw_object.ellipse([(X - sun_radius, Y - sun_radius), (X + sun_radius, Y + sun_radius)], fill = sun_color)
    else: #moon
        color: int = moon_color
        if (current_time.tm_hour < night_end_hour):
            theta: float = max_radian - ((current_time.tm_hour + night_end_hour) * 60 + current_time.tm_min) * delta_radian
        else:
            theta: float = max_radian - ((current_time.tm_hour - night_start_hour) * 60 + current_time.tm_min) * delta_radian
        X: int = int(x + r * math.cos(theta))
        Y: int = int(y - r * math.sin(theta))
        draw_object.chord([(X - sun_radius, Y - sun_radius), (X + sun_radius, Y + sun_radius)], start = -45, end = 135, fill = moon_color)

#-------------------------------------#

### main ###

if (not is_debug_mode):
    twitter_client: Twitter = Twitter(twitter_credentials_file)

font: object = ImageFont.truetype(font_name, size = font_size)

while (True):

    image: Image.Image = Image.new(color_mode, header_size, color = bg_color)
    draw_object: ImageDraw.Draw = ImageDraw.Draw(image)

    if (should_draw_sun_or_moon):
        draw_sun_or_moon(draw_object)

    draw_object.text((header_size[0] / 4, 0), text = create_date_string(), fill = fg_color, font = font)

    if (is_debug_mode):
        image = image.resize((header_size[0] // 2, header_size[1] // 2))
        image.show()
        break

    image.save(output_image_file)

    twitter_client.change_header_image_(output_image_file)

    if (interval_sec == 60): #If `interval_sec` is exactly 60 seconds, waits with a higher accuracy. For example, if you start the program at 12:43:18, the next update will be 12:44:00 instead of 12:44:18.
        time.sleep(interval_sec - time.localtime().tm_sec + 1)
    else:
        time.sleep(interval_sec)

#-------------------------------------#
