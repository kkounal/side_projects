# Captions.py

A command line tool that allows you to generate and embed subtitles to videos. Can also translate subtitles to other languages.  

Credit for some base/skeleton code goes to/this is an improvement/expansion of https://github.com/pacifio/autocap

## Installation/Dependancies

External programms: You need to have ffmpeg (and maybe ImageMagick if it doesn't work without it) installed.

Python pacakges: The script can then download all the python packages it needs automatically, 

although you might have to uninstall and install again whisper manually with pip slightly differently and change the imagemagick path for moviepy 

(see https://github.com/openai/whisper/discussions/120 and https://github.com/Zulko/moviepy/issues/378)

Tested it on windows 10 but should work on other operating systems too.

To translate srt(s) you have from other sources you might have to pass it through something like that first: 

https://stackoverflow.com/questions/56188938/how-to-convert-subtitle-file-to-have-only-one-sentence-per-subtitle  

## Usage

usage: captions.py [-h] mode [path]

auto caption generator v2.0

positional arguments:
  mode        operation mode, valid values: ('attach', 'generate', 'translate', 'all', 'youtube-a', 'youtube-g', 'youtube-all', 'caption', 'youtube-c')
  path        filepath or link of the video

options:
  -h, --help  show this help message and exit

User Manual:
====================
 functions:
    generate: generate subtitles (srt) file for a video

    attach: attach/embed a srt file to/inside a video

    caption: caption a video, (generate then attach)

    translate: translate a srt file to another language

    all: generate, translate and attach a srt file to a video

====================
====================
 usage examples:

    python3 captions.py generate <path_to_video>
    python3 captions.py attach <path_to_video> (the srt you wish to attach is assumed to be created by this script, i.e. named according to OUTPUT_SRT)

    python3 captions.py translate (the srt you wish to translate is assumed to be created by this script, i.e. named according to OUTPUT_SRT)

    python3 captions.py youtube-c <youtube_link>

    python3 captions.py youtube-all <youtube_link>

====================