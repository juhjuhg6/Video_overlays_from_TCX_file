import xml.etree.ElementTree as ET
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont
from urllib.request import urlopen
import os
import shutil
import sys


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

    return options['speed_frame_rate']['value'], options['hr_frame_rate']['value'], options['font_size']['value'], tree


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


def create_images(trackpoints, font, speed_frame_rate, hr_frame_rate):
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
                speed = str(round(speed * 3.6, 1))

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
    speed_frame_rate, hr_frame_rate, font_size, tree = init_values()

    trackpoints = parse_tcx(tree)

    font_url = 'https://github.com/googlefonts/roboto/raw/master/src/hinted/Roboto-Bold.ttf'
    font = ImageFont.truetype(urlopen(font_url), size=font_size)

    create_images(trackpoints, font, speed_frame_rate, hr_frame_rate)


main()
