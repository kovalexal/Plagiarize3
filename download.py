"""
Originally taken from
https://bitbucket.org/techtonik/python-wget/src/1caf6503dbbd1b616dc103bca37d75f0aa046a69/wget.py?at=default
"""

#!/usr/bin/env python
"""
Download utility as an easy way to get file from the net
 
  python -m wget <URL>
  python wget.py <URL>

Downloads: http://pypi.python.org/pypi/wget/
Development: http://bitbucket.org/techtonik/python-wget/

To include this module into Python library, it is better
to rename it to something like 'fetch' to avoid complains
about missing options.

Public domain by anatoly techtonik <techtonik@gmail.com>
Also available under the terms of MIT license
Copyright (c) 2010-2012 anatoly techtonik 
"""


import sys, shutil, os
import tempfile
import math

PY3K = sys.version_info >= (3, 0)
if PY3K:
  import urllib.request as urllib
  import urllib.parse as urlparse
else:
  import urllib
  import urlparse


__version__ = "1.0"


def filename_from_url(url):
    """:return: detected filename or None"""
    fname = os.path.basename(urlparse.urlparse(url).path)
    if len(fname.strip(" \n\t.")) == 0:
        return None
    return fname

def filename_from_headers(headers):
    """Detect filename from Content-Disposition headers if present.
    http://greenbytes.de/tech/tc2231/

    :param: headers as dict, list or string
    :return: filename from content-disposition header or None
    """
    if type(headers) == str:
        headers = headers.splitlines()
    if type(headers) == list:
        headers = dict([x.split(':', 1) for x in headers])
    cdisp = headers.get("Content-Disposition")
    if not cdisp:
        return None
    cdtype = cdisp.split(';')
    if len(cdtype) == 1:
        return None
    if cdtype[0].strip().lower() not in ('inline', 'attachment'):
        return None
    # several filename params is illegal, but just in case
    fnames = [x for x in cdtype[1:] if x.strip().startswith('filename=')]
    if len(fnames) > 1:
        return None
    name = fnames[0].split('=')[1].strip(' \t"')
    name = os.path.basename(name)
    if not name:
        return None
    return name

def filename_fix_existing(filename):
    """Expands name portion of filename with numeric ' (x)' suffix to
    return filename that doesn't exist already.
    """
    dirname = '.' 
    name, ext = filename.rsplit('.', 1)
    names = [x for x in os.listdir(dirname) if x.startswith(name)]
    names = [x.rsplit('.', 1)[0] for x in names]
    suffixes = [x.replace(name, '') for x in names]
    # filter suffixes that match ' (x)' pattern
    suffixes = [x[2:-1] for x in suffixes
                   if x.startswith(' (') and x.endswith(')')]
    indexes  = [int(x) for x in suffixes
                   if set(x) <= set('0123456789')]
    idx = 1
    if indexes:
        idx += sorted(indexes)[-1]
    return '%s (%d).%s' % (name, idx, ext)


def get_console_width():
    """Return width of available window area. Autodetection works for
       Windows and POSIX platforms. Returns 80 for others

       Code from http://bitbucket.org/techtonik/python-pager
    """

    if os.name == 'nt':
        STD_INPUT_HANDLE  = -10
        STD_OUTPUT_HANDLE = -11
        STD_ERROR_HANDLE  = -12

        # get console handle
        from ctypes import windll, Structure, byref
        try:
            from ctypes.wintypes import SHORT, WORD, DWORD
        except ImportError:
            # workaround for missing types in Python 2.5
            from ctypes import (
                c_short as SHORT, c_ushort as WORD, c_ulong as DWORD)
        console_handle = windll.kernel32.GetStdHandle(STD_OUTPUT_HANDLE)

        # CONSOLE_SCREEN_BUFFER_INFO Structure
        class COORD(Structure):
            _fields_ = [("X", SHORT), ("Y", SHORT)]

        class SMALL_RECT(Structure):
            _fields_ = [("Left", SHORT), ("Top", SHORT),
                        ("Right", SHORT), ("Bottom", SHORT)]

        class CONSOLE_SCREEN_BUFFER_INFO(Structure):
            _fields_ = [("dwSize", COORD),
                        ("dwCursorPosition", COORD),
                        ("wAttributes", WORD),
                        ("srWindow", SMALL_RECT),
                        ("dwMaximumWindowSize", DWORD)]

        sbi = CONSOLE_SCREEN_BUFFER_INFO()
        ret = windll.kernel32.GetConsoleScreenBufferInfo(console_handle, byref(sbi))
        if ret == 0:
            return 0
        return sbi.srWindow.Right+1

    elif os.name == 'posix':
        from fcntl import ioctl
        from termios import TIOCGWINSZ
        from array import array

        winsize = array("H", [0] * 4)
        try:
            ioctl(sys.stdout.fileno(), TIOCGWINSZ, winsize)
        except IOError:
            pass
        return (winsize[1], winsize[0])[0]

    return 80


def bar_thermometer(current, total, width=80):
    """Return thermometer style progress bar string. `total` argument
    can not be zero. The minimum size of bar returned is 3. Example:

        [..........            ]

    Control and trailing symbols (\r and spaces) are not included.
    See `bar_adaptive` for more information.
    """
    # number of dots on thermometer scale
    avail_dots = width-2
    shaded_dots = int(math.floor(float(current) / total * avail_dots))
    return '[' + '.'*shaded_dots + ' '*(avail_dots-shaded_dots) + ']'

def bar_adaptive(current, total, width=80):
    """Return progress bar string for given values in one of three
    styles depending on available width:

        [..  ] downloaded / total
        downloaded / total
        [.. ]

    if total value is unknown or <= 0, show bytes counter using two
    adaptive styles:

        %s / unknown
        %s

    if there is not enough space on the screen, do not display anything

    returned string doesn't include control characters like \r used to
    place cursor at the beginning of the line to erase previous content.

    this function leaves one free character at the end of string to
    avoid automatic linefeed on Windows.
    """

    # process special case when total size is unknown and return immediately
    if not total or total < 0:
        msg = "%s / unknown" % current
        if len(msg) < width:    # leaves one character to avoid linefeed
            return msg
        if len("%s" % current) < width:
            return "%s" % current

    min_bar_width = 3 # [.]

    if width < min_bar_width+1:  # +1 reserved to avoid linefeed on Windows
        return ''

    size_width = len("%s" % total)
    size_field_width = size_width*2 + 3 # 'xxxx / yyyy'

    # [. ] 
    if width < size_field_width+1:
        return bar_thermometer(current, total, width-1)

    full_width = min_bar_width+1+size_field_width
    size_info = "%s / %s" % (current, total)
    # padding with spaces
    size_info = " "*(size_field_width-len(size_info)) + size_info

    # downloaded / total 
    if width < full_width+1:
        return size_info

    # [..  ] downloaded / total
    bar_width = width-1-size_field_width-1
    bar = bar_thermometer(current, total, bar_width)
    return "%s %s" % (bar, size_info)


__current_size = 0  # global state variable, which exists solely as a
                    # workaround against Python 3.3.0 regression
                    # http://bugs.python.org/issue16409
def progress_callback(blocks, block_size, total_size):
    """callback function for urlretrieve that is called when connection is
    created and when once for each block

    draws adaptive progress bar in terminal/console

    use sys.stdout.write() instead of "print,", because it allows one more
    symbol at the line end without linefeed on Windows

    :param blocks: number of blocks transferred so far
    :param block_size: in bytes
    :param total_size: in bytes, can be -1 if server doesn't return it
    """
    global __current_size
 
    width = min(100, get_console_width())

    if sys.version_info[:3] == (3, 3, 0):  # regression workaround
        if blocks == 0:  # first call
            __current_size = 0
        else:
            __current_size += block_size
        current_size = __current_size
    else:
        current_size = min(blocks*block_size, total_size)
    progress = bar_adaptive(current_size, total_size, width)
    if progress:
        sys.stdout.write("\r" + progress)


def download(url, directory = ".", callback=progress_callback):
    """High level function, which downloads URL into tmp file in current
    directory and then renames it to filename autodetected from either URL
    or HTTP headers.

    :return:  filename where URL is downloaded to
    """

    if directory.endswith("/"):
        directory = directory[:-1]

    print("\nDownloading:\n{0}\n".format(url))

    filename = filename_from_url(url) or "."
    # get filename for temp file in current directory
    (fd, tmpfile) = tempfile.mkstemp(".tmp", prefix=filename+".", dir="./TMP/")
    os.close(fd)
    os.unlink(tmpfile)

    try:
        (tmpfile, headers) = urllib.urlretrieve(url, tmpfile, callback)
    except KeyboardInterrupt:
        exit(0)
    except:
        print("Can`t download!\n{0}\n".format(url))
        return ""
    filenamealt = filename_from_headers(headers)
    if filenamealt:
        filename = filenamealt
    filename = directory + "/" + filename
    # add numeric ' (x)' suffix if filename already exists
    if os.path.exists(filename):
        filename = filename_fix_existing(filename)
    shutil.move(tmpfile, filename)

    #print headers
    return filename


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit("No download URL specified")

    url = sys.argv[1]
    filename = download(url, progress_callback)

    print("")
    print("Saved under %s" % filename)

r"""
features that require more tuits for urlretrieve API
http://www.python.org/doc/2.6/library/urllib.html#urllib.urlretrieve

[x] autodetect filename from URL
[x] autodetect filename from headers - Content-Disposition
    http://greenbytes.de/tech/tc2231/
[ ] make HEAD request to detect temp filename from Content-Disposition
[ ] process HTTP status codes (i.e. 404 error)
    http://ftp.de.debian.org/debian/pool/iso-codes_3.24.2.orig.tar.bz2
[ ] catch KeyboardInterrupt
[ ] optionally preserve incomplete file
[x] create temp file in current directory
[ ] resume download (broken connection)
[ ] resume download (incomplete file)
[x] show progress indicator
    http://mail.python.org/pipermail/tutor/2005-May/038797.html
[x] do not overwrite downloaded file
 [x] rename file automatically if exists
[ ] optionally specify path for downloaded file

[ ] options plan
[ ] clbr progress bar style
[ ] process Python 2.x urllib.ContentTooShortError exception gracefully
    (ideally retry and continue download)

    (tmpfile, headers) = urllib.urlretrieve(url, tmpfile, progress_callback)
  File "C:\Python27\lib\urllib.py", line 93, in urlretrieve
    return _urlopener.retrieve(url, filename, reporthook, data)
  File "C:\Python27\lib\urllib.py", line 283, in retrieve
    "of %i bytes" % (read, size), result)
urllib.ContentTooShortError: retrieval incomplete: got only 15239952 out of 24807571 bytes

[ ] find out if urlretrieve may return unicode headers
[ ] test suite for unsafe filenames from url and from headers
"""
