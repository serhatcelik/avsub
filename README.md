# AVsub
A simplified command-line interface for FFmpeg.

## OS Support
- GNU/Linux
- Microsoft Windows

## Requirements
- Python ~=3.5
- FFmpeg (the latest version is recommended)

## Preparation and Installation
```
$ pip3 install --upgrade pip
$ pip3 install --upgrade setuptools
$ pip3 install --upgrade avsub
```

Note: If you want to use the program by downloading directly from GitHub without installing it from PyPI, do the following:

```
$ git clone https://github.com/serhatcelik/avsub.git
$ cd avsub
$ python3 -m avsub --help
```

## Usage
```
$ avsub --help
```

```
usage: avsub [-h] [+a CODEC] [+s CODEC] [+v CODEC] [-A] [--channel CHANNEL]
             [--compress VALUE] [--copy STREAM [STREAM ...]] [-F] [-H] [-i]
             [-L] [--remove STREAM [STREAM ...]] [--speed PRESET] [-S] [-v]
             [-V] [-b] [--color1 COLOR] [--color2 COLOR] [--embed SUBTITLE]
             [--font NAME] [--position POSITION] [--size VALUE]
             input extension

AVsub - A simplified command-line interface for FFmpeg
Written by Serhat Çelik (with the help of my family and a friend)

positional arguments:
  input                 input file or folder
  extension             output extension

optional arguments:
  -h, --help            show this help message and exit
  +a CODEC              set CODEC as output audio codec
  +s CODEC              set CODEC as output subtitle codec
  +v CODEC              set CODEC as output video codec
  -A, --audio           choose audio stream(s) only
  --channel CHANNEL     set CHANNEL as output audio channel
  --compress VALUE      set VALUE as crf value to compress video
  --copy STREAM [STREAM ...]
                        use copy codec for output STREAM instead of another codec
  -F, --ffmpeg          show the ffmpeg command during processing (except auto/hardsub)
  -H, --hidden          include hidden input
  -i, --inform          show informative messages during processing
  -L, --license         show license and exit
  --remove STREAM [STREAM ...]
                        do not copy STREAM from input to output
  --speed PRESET        set PRESET as video encoding speed
  -S, --subtitle        choose subtitle stream(s) only
  -v, --version         show program version and exit
  -V, --video           choose video stream(s) only

subtitle arguments:
  -b, --box             add an opaque box around subtitle
  --color1 COLOR        set COLOR as subtitle primary color [default: white]
  --color2 COLOR        set COLOR as subtitle outline color [default: black]
  --embed SUBTITLE      embed SUBTITLE into video
  --font NAME           set NAME as subtitle font name
  --position POSITION   set POSITION as subtitle alignment [default: bottom]
  --size VALUE          set VALUE as subtitle font size [default: 20]

This tool is for basic operations only. If you need advanced operations, use FFmpeg instead.
See https://github.com/serhatcelik/avsub for more information.
```

## Examples
```
Convert mkv to mp4
$ avsub input.mkv mp4

Convert all files in current directory to mp4 including hidden ones
$ avsub . mp4 --hidden

Convert mkv to mp4 with audio codec aac
$ avsub input.mkv mp4 +a aac

Convert mp4 to mp3 and choose audio stream only
$ avsub input.mp4 mp3 --audio

Compress video with CRF (Constant Rate Factor) value 30
$ avsub input.mp4 mp4 --compress 30

Copy video and subtitle stream from input to output
$ avsub input.mp4 mp4 --copy video sub

Do not copy subtitle stream and metadata from input to output
$ avsub input.mp4 mp4 --remove sub metadata

Embed subtitle into video with font name Arial and font size 25
$ avsub input.mp4 mp4 --embed input.srt --font "Arial" --size 25

Embed subtitle into video with primary color red and outline color blue
$ avsub input.mp4 mp4 --embed input.srt --color1 red --color2 blue
```

## License
[GNU General Public License v3.0](https://choosealicense.com/licenses/gpl-3.0/)

## Feedback
If you have found a bug or have a suggestion, please consider creating an issue.
