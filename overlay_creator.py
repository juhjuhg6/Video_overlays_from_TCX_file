import xml.etree.ElementTree as ET
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont
from urllib.request import urlopen
import os
import shutil
import sys


SPEED_PARAMETERS = {
    '0': { # for km/h
        'multiplier': 3.6,
        'power': 1,
    },
    '1': { # for min/km
        'multiplier': 100/6,
        'power': -1
    },
    '2': { # for m/s
        'multiplier': 1,
        'power': 1
    },
    '3': { # for mph
        'multiplier': 2.23693629,
        'power': 1
    }
}


def init_values():
    while True:
        filename = input('Path of the TCX file: ')
        try:
            tree = ET.parse(filename)
            break
        except FileNotFoundError:
            print('Invalid path or filename')
            continue
        except:
            print('Invalid file')
            continue

    while True:
        user_input = input('Choose speed unit (0 = km/h, 1 = min/km, 2 = m/s, 3 = mph, default is km/h): ')
        if user_input in ['0', '1', '2', '3']:
            speed_unit = user_input
            break
        elif user_input == '':
            speed_unit = '0'
            break
        print('Invalid input')

    options = {
        'speed_frame_rate': {
            'input text': 'Choose speed frame rate (0 for no frames, default: 2): ',
            'value': 2
        },
        'hr_frame_rate': {
            'input text': 'Choose heart rate frame rate (0 for no frames, default: 1): ',
            'value': 1
        },
        'font_size': {
            'input text': 'Choose font size (default: 100): ',
            'value': 100
        }
    }

    for key, value in options.items():
        while True:
            user_input = input(value['input text'])
            try:
                value['value'] = int(user_input)
                break
            except ValueError:
                if user_input == '':
                    break
                else:
                    print('Invalid value')
                    continue

    return options['speed_frame_rate']['value'], options['hr_frame_rate']['value'], options['font_size']['value'],\
           tree, speed_unit


def parse_tcx(tree):
    root = tree.getroot()

    ns = {'ns': 'http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2',
          'ns3': 'http://www.garmin.com/xmlschemas/ActivityExtension/v2'}

    trackpoints = []

    for trackpoint in root.findall('.//ns:Trackpoint', ns):
        trackpoint_dict = {}

        tp_time_elem = trackpoint.find('ns:Time', ns)
        tp_hr_elem = trackpoint.find('ns:HeartRateBpm/ns:Value', ns)
        tp_speed_elem = trackpoint.find('.//ns:Extensions/ns3:TPX/ns3:Speed', ns)

        if tp_time_elem is not None:
            trackpoint_dict['time'] = datetime.strptime(tp_time_elem.text, '%Y-%m-%dT%H:%M:%S.%fZ')
        if tp_hr_elem is not None:
            trackpoint_dict['hr'] = int(tp_hr_elem.text)
        if tp_speed_elem is not None:
            trackpoint_dict['speed'] = float(tp_speed_elem.text)

        trackpoints.append(trackpoint_dict)

    return trackpoints


def create_images(trackpoints, font, speed_frame_rate, hr_frame_rate, speed_unit):
    sys.stdout.write('Deleting old images...')

    if os.path.exists('speed'):
        shutil.rmtree('speed')
    os.mkdir('speed')

    if os.path.exists('heart_rate'):
        shutil.rmtree('heart_rate')
    os.mkdir('heart_rate')

    sys.stdout.write('\rGenerating images, 0 % done')

    for i in range(len(trackpoints) - 1):
        trackpoint = trackpoints[i]
        next_trackpoint = trackpoints[i+1]
        trackpoint_time_diff = next_trackpoint['time'] - trackpoint['time']

        # speed
        for j in range(trackpoint_time_diff.seconds * speed_frame_rate):
            if not ('speed' in trackpoint) or not ('speed' in next_trackpoint):
                # to keep timing right, output empty frames if speed is not available in some trackpoints
                speed = ' '
            else:
                # speed changes linearly between trackpoints
                speed = trackpoint['speed'] + (next_trackpoint['speed'] - trackpoint['speed']) * j\
                        / (trackpoint_time_diff.seconds * speed_frame_rate)
                if speed == 0:
                    speed = str(speed)
                else:
                    speed = str(round(pow(speed, SPEED_PARAMETERS[speed_unit]['power'])
                                      * SPEED_PARAMETERS[speed_unit]['multiplier'], 1))

            frame_index = (trackpoint['time'] - trackpoints[0]['time']).seconds * speed_frame_rate + j
            speed_frame = Image.new('RGBA', font.getsize(speed), (255, 255, 255, 0))
            ImageDraw.Draw(speed_frame).text((0, 0), speed, font=font, fill=(255, 255, 255, 255))
            speed_frame.save('speed/speed.' + str(frame_index) + '.png')

        # heart rate
        for j in range(trackpoint_time_diff.seconds * hr_frame_rate):
            if not ('hr' in trackpoint) or not ('hr' in next_trackpoint):
                # to keep timing right, output empty frames if heart rate is not available in some trackpoints
                hr = ' '
            else:
                # heart rate changes linearly between trackpoints
                hr = trackpoint['hr'] + (next_trackpoint['hr'] - trackpoint['hr']) * j\
                     / (trackpoint_time_diff.seconds * hr_frame_rate)
                hr = str(int(hr))

            frame_index = (trackpoint['time'] - trackpoints[0]['time']).seconds * hr_frame_rate + j
            hr_frame = Image.new('RGBA', font.getsize(hr), (255, 255, 255, 0))
            ImageDraw.Draw(hr_frame).text((0, 0), hr, font=font, fill=(255, 255, 255, 255))
            hr_frame.save('heart_rate/heart_rate.' + str(frame_index) + '.png')

        progress = (next_trackpoint['time'] - trackpoints[0]['time']).seconds /\
                   (trackpoints[-1]['time'] - trackpoints[0]['time']).seconds * 100
        sys.stdout.write('\rGenerating images, ' + str(int(progress)) + ' % done')


def main():
    speed_frame_rate, hr_frame_rate, font_size, tree, speed_unit = init_values()

    trackpoints = parse_tcx(tree)

    font_url = 'https://github.com/googlefonts/roboto/raw/master/src/hinted/Roboto-Bold.ttf'
    font = ImageFont.truetype(urlopen(font_url), size=font_size)

    create_images(trackpoints, font, speed_frame_rate, hr_frame_rate, speed_unit)


main()
