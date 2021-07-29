# AVsub

AVsub is a simplified command-line interface for FFmpeg. It supports [Python 3][1] (3.5 to 3.9) and requires [FFmpeg][2] to be installed to run. It is intended to be cross platform, and runs on GNU/Linux and Microsoft Windows.

## Preparation and Installation

### PyPI

```shell
$ pip3 install -U pip
$ pip3 install -U setuptools
$ pip3 install -U avsub
```

Note: You may need to [configure your PATH][3] after installation.

### GitHub

```shell
$ git clone https://github.com/serhatcelik/avsub.git
$ cd avsub
$ python3 -m avsub --help
```

## Usage

```shell
$ avsub --help
```

```
usage: avsub [input extension [extra_arguments]]

AVsub - A simplified command-line interface for FFmpeg
Written by Serhat Çelik (with the help of my family and a friend)

positional arguments:
  input                 input file or folder
  extension             output extension ('-' for input file extension)

optional arguments:
  -h, --help            show this help message and exit
  +a CODEC              set CODEC as output audio codec
  -A, --audio           choose audio stream(s) only
  --channel CHANNEL     set CHANNEL as output audio channel
  -C [VALUE], --compress [VALUE]
                        set VALUE as crf value to compress video [constant: 30]
  -c STREAM [STREAM ...], --copy STREAM [STREAM ...]
                        use copy codec for output STREAM instead of another codec
  -f ARGS               provide ARGS as a custom ffmpeg argument list (be careful!!)
  --no-map-all          disable choosing all streams (may cause data loss)
  --remove STREAM [STREAM ...]
                        do not copy STREAM from input to output
  +s CODEC              set CODEC as output subtitle codec
  --speed PRESET        set PRESET as video encoding speed
  -S, --subtitle        choose subtitle stream(s) only
  --trim FROM TO        extract a portion of input from second FROM to TO
  +v CODEC              set CODEC as output video codec
  -V, --video           choose video stream(s) only

hardsub arguments:
  -b, --box             add an opaque box around subtitle
  --color1 COLOR        set COLOR as subtitle primary color [default: white]
  --color2 COLOR        set COLOR as subtitle outline color [default: black]
  -e SUBTITLE, --embed SUBTITLE
                        embed SUBTITLE into video
  --font NAME           set NAME as subtitle font name
  --position POSITION   set POSITION as subtitle alignment [default: bottom]
  --size VALUE          set VALUE as subtitle font size [default: 20]

independent arguments:
  -B, --bypass          skip checking some command-line arguments (not recommended)
  --exclude EXTENSION [EXTENSION ...]
                        do not process input if its extension is EXTENSION
  -F, --ffmpeg          show the ffmpeg command during processing
  -H, --hidden          include hidden input
  -i, --inform          show informative messages during processing (can be increased)
  -L, --license         show license and exit
  --no-open-dir         do not open the output folder at the end (active for gnu/linux)
  --only EXTENSION [EXTENSION ...]
                        process input only if its extension is EXTENSION
  -v, --version         show program version and exit

This tool is for basic operations only. If you need advanced operations, use FFmpeg instead.
See https://github.com/serhatcelik/avsub for more information.
```

## Examples

```shell
# Convert mkv to mp4
avsub "input.mkv" mp4

# Convert all files in current directory to mp4 including hidden ones
avsub . mp4 -H

# Convert mkv to mp4 with audio codec aac
avsub "input.mkv" mp4 +a aac

# Convert mp4 to mp3 and choose audio stream only
avsub "input.mp4" mp3 -A

# Compress video with CRF (Constant Rate Factor) value 35
avsub "input.mp4" mp4 --compress 35

# Copy audio and video stream from input to output
avsub "input.mp4" mp4 --copy audio video

# Do not copy subtitle stream and metadata from input to output
avsub "input.mp4" mp4 --remove sub metadata

# Embed subtitle into video (hardsub) with font name Arial and font size 25
avsub "input.mp4" mp4 --embed "input.srt" --font "Arial" --size 25

# Embed subtitle into video with primary color red and outline color blue
avsub "input.mp4" mp4 --embed "input.srt" --color1 red --color2 blue

# Provide a custom FFmpeg argument list -at your own risk- to limit the output bit rate
avsub "input.mp4" mp4 -f="-b:v 2M -maxrate 2M -bufsize 1M"
```

## License

[GNU General Public License v3.0][4]

## Feedback

If you have found a bug or have a suggestion, please consider [creating an issue][5].


[1]: https://www.python.org
[2]: https://ffmpeg.org
[3]: https://github.com/serhatcelik/avsub/wiki/Windows-PATH
[4]: https://choosealicense.com/licenses/gpl-3.0/
[5]: https://github.com/serhatcelik/avsub/issues
