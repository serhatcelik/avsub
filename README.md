# AVsub

[![QUALITY](https://img.shields.io/codacy/grade/e4743ffb247d48c399d5b92c6bdeaa4b?label=Quality&style=flat-square "QUALITY")][8]
[![VERSION](https://img.shields.io/pypi/v/avsub?label=PyPI&style=flat-square "VERSION")][7]
[![REQUIRES](https://img.shields.io/pypi/pyversions/avsub?label=Python&style=flat-square "REQUIRES")][7]
[![LICENSE](https://img.shields.io/pypi/l/avsub?label=License&style=flat-square "LICENSE")][4]

**AVsub is a simplified command-line interface for [FFmpeg][2]. It supports
[Python 3][1] and requires FFmpeg to run, also intended to be
cross-platform, and runs on GNU/Linux and Microsoft Windows.**

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
python -m avsub -h
```

## Usage

Use the following command to get [usage][6] help:

```shell
avsub -h
```

## Examples

```shell
# Convert mkv to mp4
avsub "input.mkv" mp4

# Convert all files in current directory to mp4 including hidden ones
avsub . mp4 -H

# Copy video stream from input to output, keep input extension
avsub "input.mp4" - -c video

# Convert mkv to mp4 with audio codec aac and video codec h264
avsub "input.mkv" mp4 +a aac +v h264

# Convert mp4 to mp3 and choose audio stream (not other streams)
avsub "input.mp4" mp3 -A

# Compress video with CRF (Constant Rate Factor) value of 35
avsub "input.mp4" - -C 35

# Do not copy subtitle stream and metadata from input to output
avsub "input.mp4" - --remove sub metadata

# Extract a part of video from 02:01:00 (or 7260) to 02:01:05 (or 7265)
avsub "input.mp4" - --trim 02:01:00 02:01:05

# Embed subtitle into video (hardsub) with font name Arial and font size 25
avsub "input.mp4" - -e "input.srt" --font "Arial" --size 25

# Embed subtitle into video with primary color red and outline color blue
avsub "input.mp4" - -e "input.srt" --color1 red --color2 blue

# Provide an FFmpeg argument list -at your own risk- to limit the bit rate
avsub "input.mp4" - -f="-b:v 2M -maxrate 2M -bufsize 1M"
```

## Feedback

If you have found a bug or have a suggestion, please consider
[creating an issue][5].

[1]: https://www.python.org
[2]: https://ffmpeg.org
[3]: https://github.com/serhatcelik/avsub/wiki/Windows-PATH
[4]: https://choosealicense.com/licenses/gpl-3.0/
[5]: https://github.com/serhatcelik/avsub/issues
[6]: https://github.com/serhatcelik/avsub/wiki#usage
[7]: https://pypi.org/project/avsub/
[8]: https://www.codacy.com/gh/serhatcelik/avsub
