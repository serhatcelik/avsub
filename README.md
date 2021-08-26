# AVsub

[![](https://img.shields.io/badge/thank-serhatcelik-1EAEDB.svg)][saythanks]

**AVsub is a simplified command-line interface for FFmpeg. It supports [Python 3][1] (3.6 to 3.9) and requires [FFmpeg][2] to be installed to run. It is intended to be cross platform, and runs on GNU/Linux and Microsoft Windows.**

## Preparation and Installation

Note: On GNU/Linux, change the command "python" to "python3".

### PyPI

```shell
python -m pip install -U pip
python -m pip install -U setuptools
python -m pip install -U avsub
```

Note: You may need to [configure your Windows PATH][3] after installation.

### GitHub

```shell
git clone https://github.com/serhatcelik/avsub.git
cd avsub
python -m avsub --help
```

## Usage

Use the following command to get [usage][6] help:

```shell
avsub --help
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


[saythanks]: https://saythanks.io/to/serhatcelik
[1]: https://www.python.org
[2]: https://ffmpeg.org
[3]: https://github.com/serhatcelik/avsub/wiki/Windows-PATH
[4]: https://choosealicense.com/licenses/gpl-3.0/
[5]: https://github.com/serhatcelik/avsub/issues
[6]: https://github.com/serhatcelik/avsub/wiki#usage
