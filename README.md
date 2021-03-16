# AVsub

A simplified CLI for FFmpeg.

## OS Support

- GNU/Linux
- Microsoft Windows

## Requirements

- Python ~=3.5
- FFmpeg

## Preparation and Installation

Note: If you are using a Windows operating system, you may need to configure your PATH after installation.

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
usage: avsub [-h] [+a CODEC] [-A] [--compress VALUE] [--copy STREAM [STREAM ...]] [-H]
             [-i] [-L] [--remove STREAM [STREAM ...]] [+s CODEC] [--speed PRESET] [-S]
             [+v CODEC] [-v] [-V] [-b] [--color1 COLOR] [--color2 COLOR] [--embed SUBTITLE]
             [--font NAME] [--position POSITION] [--size VALUE]
             INPUT EXTENSION

AVsub : A simplified CLI for FFmpeg
Written by Serhat Çelik (with the help of my family and a friend)

positional arguments:
  INPUT                 input file or folder
  EXTENSION             output extension

optional arguments:
  -h, --help            show this help message and exit
  +a CODEC              set CODEC as output audio codec
  -A, --audio           choose audio stream(s) only
  --compress VALUE      set VALUE as crf value to compress input
  --copy STREAM [STREAM ...]
                        use copy codec for output STREAM instead of another codec
  -H, --hidden          include hidden input (note: root folders are considered hidden)
  -i, --inform          show informative messages during processing
  -L, --license         show license and exit
  --remove STREAM [STREAM ...]
                        do not copy STREAM from input to output
  +s CODEC              set CODEC as output subtitle codec
  --speed PRESET        set PRESET as encoding speed
  -S, --subtitle        choose subtitle stream(s) only
  +v CODEC              set CODEC as output video codec
  -v, --version         show program version and exit
  -V, --video           choose video stream(s) only

subtitle arguments:
  -b, --box             add an opaque box around subtitle
  --color1 COLOR        set COLOR as subtitle primary color [default: white]
  --color2 COLOR        set COLOR as subtitle outline color [default: black]
  --embed SUBTITLE      embed SUBTITLE into video
  --font NAME           set NAME as subtitle font name
  --position POSITION   set POSITION as subtitle alignment [default: bottom]
  --size VALUE          set VALUE as subtitle font size [default: 18]

This tool is for very basic operations only. If you need advanced operations, use FFmpeg instead.
See https://github.com/serhatcelik/avsub for more information.
```

## License

[GNU General Public License v3.0](https://choosealicense.com/licenses/gpl-3.0/)

## Feedback

If you have found a bug or have a suggestion, please consider creating an issue.
