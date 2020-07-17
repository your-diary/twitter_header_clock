#-------------------------------------#

### import ###

import sys
import os
import time
import subprocess
import json
import signal
import random

from PIL import Image, ImageDraw, ImageFont
import twitter

#-------------------------------------#

### Parameters ###

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

color_mode: str = 'L'
bg_color: int = 0x3C
fg_color: int = 0xDD

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

#-------------------------------------#

### main ###

twitter_client: Twitter = Twitter(twitter_credentials_file)

font: object = ImageFont.truetype(font_name, size = font_size)

while (True):

    image: Image.Image = Image.new(color_mode, header_size, color = bg_color)
    draw_object: ImageDraw.Draw = ImageDraw.Draw(image)
    draw_object.text((header_size[0] / 4, 0), text = create_date_string(), fill = fg_color, font = font)
    image.save(output_image_file)

    twitter_client.change_header_image_(output_image_file)

    time.sleep(interval_sec)

#-------------------------------------#

