"""
Setup script for AVsub.
"""

import setuptools

with open("README.md", "r", encoding="utf-8") as readme:
    long_description = readme.read()

setuptools.setup(
    name="avsub",
    version=__import__("avsub.__license__", fromlist="__license__").VERSION,
    description="A simplified command-line interface for FFmpeg",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author=__import__("avsub.__license__", fromlist="__license__").AUTHOR,
    url="https://github.com/serhatcelik/avsub",
    download_url="https://github.com/serhatcelik/avsub/releases/latest",
    packages=setuptools.find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Console",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Natural Language :: English",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: Microsoft :: Windows :: Windows 7",
        "Operating System :: Microsoft :: Windows :: Windows 8",
        "Operating System :: Microsoft :: Windows :: Windows 8.1",
        "Operating System :: Microsoft :: Windows :: Windows 10",
        "Operating System :: POSIX",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Topic :: Multimedia",
        "Topic :: Multimedia :: Sound/Audio",
        "Topic :: Multimedia :: Sound/Audio :: Conversion",
        "Topic :: Multimedia :: Video",
        "Topic :: Multimedia :: Video :: Conversion",
    ],
    options={
        "build_scripts": {
            "executable": "/bin/custom_python",
        },
    },
    license=__import__("avsub.__license__", fromlist="__license__").LICENSE,
    license_files=["LICENSE"],
    keywords=["avsub", "audio", "video", "subtitle", "ffmpeg"],
    platforms=["Linux", "Windows"],
    zip_safe=False,
    entry_points={
        "console_scripts": [
            "avsub = avsub.__main__:setup_py_main",
        ],
    },
    python_requires="~=3.6",
    project_urls={
        "Source Code": "https://github.com/serhatcelik/avsub",
        "Bug Tracker": "https://github.com/serhatcelik/avsub/issues",
        "Documentation": "https://github.com/serhatcelik/avsub/wiki",
    },
)
