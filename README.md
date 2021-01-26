# Video_overlays_from_TCX_file

This is a command line tool for creating video overlays from sports activity data.
Script creates PNG image sequences from speed and heart rate data whitch then can be imported to video editor.

## Supported files

This tool is developed to work with TCX files exported from Garmin Connect.
TCX files from other sources might not work.

However if you have uncompatible TCX file or your activity is in some other format (such as GPX of FIT) you might be
able to use it by first uploading the activity file of any format to Garmin Connect and then downloading the activity
as TCX file from there.

## Usage

**Prerequisite:** Python 3 installed

Tool has been tested in Windows 10 with Python 3.8

1. Clone or download this repository

2. Install [Pillow](https://python-pillow.org/)

```bash
python -m pip install --upgrade Pillow
```

3. Run overlay_creator.py and follow the command line instructions

```bash
python overlay_creator.py
```

4. Once the process is finished you can find generated image sequences for speed and heart rate from directories with
corresponding names located in the same directory as overlay_creator.py. You can now import these image sequences to
your video editor.