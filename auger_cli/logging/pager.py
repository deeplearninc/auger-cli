#!/usr/bin/env python
import os,sys
from math import ceil

WINDOWS = os.name == 'nt'
PY3K = sys.version_info >= (3,)

# Windows constants
# http://msdn.microsoft.com/en-us/library/ms683231%28v=VS.85%29.aspx

STD_INPUT_HANDLE  = -10
STD_OUTPUT_HANDLE = -11
STD_ERROR_HANDLE  = -12


# --- console/window operations ---

if WINDOWS:
    # get console handle
    from ctypes import windll, Structure, byref
    try:
        from ctypes.wintypes import SHORT, WORD, DWORD
    # workaround for missing types in Python 2.5
    except ImportError:
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


def _windows_get_window_size():
    """Return (width, height) of available window area on Windows.
       (0, 0) if no console is allocated.
    """
    sbi = CONSOLE_SCREEN_BUFFER_INFO()
    ret = windll.kernel32.GetConsoleScreenBufferInfo(console_handle, byref(sbi))
    if ret == 0:
        return (0, 0)
    return (sbi.srWindow.Right - sbi.srWindow.Left + 1,
            sbi.srWindow.Bottom - sbi.srWindow.Top + 1)

def _posix_get_window_size():
    """Return (width, height) of console terminal on POSIX system.
       (0, 0) on IOError, i.e. when no console is allocated.
    """
    # see README.txt for reference information
    # http://www.kernel.org/doc/man-pages/online/pages/man4/tty_ioctl.4.html

    from fcntl import ioctl
    from termios import TIOCGWINSZ
    from array import array

    """
    struct winsize {
        unsigned short ws_row;
        unsigned short ws_col;
        unsigned short ws_xpixel;   /* unused */
        unsigned short ws_ypixel;   /* unused */
    };
    """
    winsize = array("H", [0] * 4)
    try:
        ioctl(sys.stdout.fileno(), TIOCGWINSZ, winsize)
    except IOError:
        # for example IOError: [Errno 25] Inappropriate ioctl for device
        # when output is redirected
        # [ ] TODO: check fd with os.isatty
        pass
    return (winsize[1], winsize[0])

def getwidth():
    """
    Return width of available window in characters.  If detection fails,
    return value of standard width 80.  Coordinate of the last character
    on a line is -1 from returned value. 

    Windows part uses console API through ctypes module.
    *nix part uses termios ioctl TIOCGWINSZ call.
    """
    width = None
    if WINDOWS:
        return _windows_get_window_size()[0]
    elif os.name == 'posix':
        return _posix_get_window_size()[0]
    else:
        # 'mac', 'os2', 'ce', 'java', 'riscos' need implementations
        pass

    return width or 80

def getheight():
    """
    Return available window height in characters or 25 if detection fails.
    Coordinate of the last line is -1 from returned value. 

    Windows part uses console API through ctypes module.
    *nix part uses termios ioctl TIOCGWINSZ call.
    """
    height = None
    if WINDOWS:
        return _windows_get_window_size()[1]
    elif os.name == 'posix':
        return _posix_get_window_size()[1]
    else:
        # 'mac', 'os2', 'ce', 'java', 'riscos' need implementations
        pass

    return height or 25


# --- keyboard input operations and constants ---
# constants for getch() (these end with _)

if WINDOWS:
    ENTER_ = '\x0d'
    CTRL_C_ = '\x03'
else:
    ENTER_ = '\n'
    # [ ] check CTRL_C_ on Linux
    CTRL_C_ = None
ESC_ = '\x1b'

# other constants with getchars()
if WINDOWS:
    LEFT =  ['\xe0', 'K']
    UP =    ['\xe0', 'H']
    RIGHT = ['\xe0', 'M']
    DOWN =  ['\xe0', 'P']
    PG_UP = ['\xe0', 'I']
    PG_DOWN=['\xe0', 'Q']
    HOME =  ['\xe0', 'G']
    END =   ['\xe0', 'O']
else:
    LEFT =  ['\x1b', '[', 'D']
    UP =    ['\x1b', '[', 'A']
    RIGHT = ['\x1b', '[', 'C']
    DOWN =  ['\x1b', '[', 'B']
    PG_UP = ['\x1b', '[', '5', '~']
    PG_DOWN=['\x1b', '[', '6', '~']
    # HOME =  ['\x1b', '[', '1', '~']
    HOME =  ['\x1b', '[', 'H']
    # END =   ['\x1b', '[', '4', '~']
    END =   ['\x1b', '[', 'F']
ENTER = [ENTER_]
ESC  = [ESC_]

def dumpkey(key):
    """
    Helper to convert result of `getch` (string) or `getchars` (list)
    to hex string.
    """
    def hex3fy(key):
        """Helper to convert string into hex string (Python 3 compatible)"""
        from binascii import hexlify
        # Python 3 strings are no longer binary, encode them for hexlify()
        if PY3K:
           key = key.encode('utf-8')
        keyhex = hexlify(key).upper()
        if PY3K:
           keyhex = keyhex.decode('utf-8')
        return keyhex
    if type(key) == str:
        return hex3fy(key)
    else:
        return ' '.join( [hex3fy(s) for s in key] )


if WINDOWS:
    if PY3K:
        from msvcrt import kbhit, getwch as __getchw
    else:
        from msvcrt import kbhit, getch as __getchw

def _getch_windows(_getall=False):
    chars = [__getchw()]  # wait for the keypress
    if _getall:           # read everything, return list
        while kbhit():
            chars.append(__getchw())
        return chars
    else:
        return chars[0]


# [ ] _getch_linux() or _getch_posix()? (test on FreeBSD and MacOS)
def _getch_unix(_getall=False):
    """
    # --- current algorithm ---
    # 1. switch to char-by-char input mode
    # 2. turn off echo
    # 3. wait for at least one char to appear
    # 4. read the rest of the character buffer (_getall=True)
    # 5. return list of characters (_getall on)
    #        or a single char (_getall off)
    """
    import termios

    # controlling terminal owns keyboard input even when stdin is
    # redirected, see
    # https://bitbucket.org/techtonik/python-pager/issues/7/33-piping-input-doesnt-work-for-linux
    cterm = open(os.ctermid(), 'r')

    fd = cterm.fileno()
    # save old terminal settings
    old_settings = termios.tcgetattr(fd)

    chars = []
    try:
        # change terminal settings - turn off canonical mode and echo.
        # in canonical mode read from stdin returns one line at a time
        # and we need one char at a time (see DESIGN.rst for more info)
        newattr = list(old_settings)
        newattr[3] &= ~termios.ICANON
        newattr[3] &= ~termios.ECHO
        newattr[6][termios.VMIN] = 1   # block until one char received
        newattr[6][termios.VTIME] = 0
        # TCSANOW below means apply settings immediately
        termios.tcsetattr(fd, termios.TCSANOW, newattr)

        # operating on stdin fails when stdin is redirected, like
        #     ls -la | pager.py
        ch = cterm.read(1)
        chars = [ch]

        if _getall:
            # move rest of chars (if any) from input buffer
            # change terminal settings - enable non-blocking read
            newattr = termios.tcgetattr(fd)
            newattr[6][termios.VMIN] = 0      # CC structure
            newattr[6][termios.VTIME] = 0
            termios.tcsetattr(fd, termios.TCSANOW, newattr)

            while True:
                ch = cterm.read(1)
                if ch != '':
                    chars.append(ch)
                else:
                    break
    finally:
        # restore terminal settings. Do this when all output is
        # finished - TCSADRAIN flag
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        cterm.close()

    if _getall:
        return chars
    else:
        return chars[0]


# choose correct getch function at module import time
if WINDOWS:
    getch = _getch_windows
else:
    getch = _getch_unix

getch.__doc__ = \
    """
    Wait for keypress, return first char generated as a result.

    Arrows and special keys generate sequence of chars. Use `getchars`
    function to receive all chars generated or present in buffer.
    """

    # check that Ctrl-C and Ctrl-Break break this function
    #
    # Ctrl-C       [n] Windows  [y] Linux  [ ] OSX
    # Ctrl-Break   [y] Windows  [n] Linux  [ ] OSX


# [ ] check if getchars returns chars already present in buffer
#     before the call to this function
def getchars():
    """
    Wait for keypress. Return list of chars generated as a result.
    More than one char in result list is returned when arrows and
    special keys are pressed. Returned sequences differ between
    platforms, so use constants defined in this module to guess
    correct keys.
    """
    return getch(_getall=True)
    

def echo(msg):
    """
    Print msg to the screen without linefeed and flush the output.
    
    Standard print() function doesn't flush, see:
    https://groups.google.com/forum/#!topic/python-ideas/8vLtBO4rzBU
    """
    sys.stdout.write(msg)
    sys.stdout.flush()

def prompt(line_num, content_length, height):
    """
    Show default prompt to continue and process keypress.

    It assumes terminal/console understands carriage return \r character.
    """
    current_page = ceil((line_num + (height // 2)) / height)
    pages_count = ceil(content_length / height)
    prompt = "Page -%s of %s-. Press PgUP, PgDOWN, Up, Down for navigation, q or Ctrl-C to Exit . . . " % (current_page, pages_count)
    echo(prompt)
    c = getchars()
    if c in [ESC, [CTRL_C_], ['q'], ['Q']]:
        return False
    echo('\r' + ' '*(len(prompt)-1) + '\r')
    MAX_LINE = ceil(content_length-(height/2))
    if c in [PG_UP]:
        return max(1, line_num-height)
    if c in [UP]:
        return max(1, line_num-1)
    if c in [PG_DOWN]:
        return min(line_num+height, max(1, MAX_LINE-1))
    if c in [DOWN]:
        return min(line_num+1, max(1, MAX_LINE))
    if c in [HOME,]:
        return 1
    if c in [END,]:
        return MAX_LINE-1

def wrap_lines(line, width):
    # divide long lines into sublines
    # has to be done upon write due to page numbering
    # wrap long line, splitting it into sublines
    for i in range(0, len(line), width):
        yield line[i:i+width]

def page(content, pagecallback=prompt, line_num=None):
    """
    Output `content`, call `pagecallback` after every page with page
    number as a parameter. `pagecallback` may return False to terminate
    pagination.

    Default callback shows prompt, waits for keypress and aborts on
    'q', ESC or Ctrl-C.
    """
    width = getwidth()
    height = getheight()
    content_length = len(content)

    if line_num is None or line_num == -1:
        line_num = ceil(content_length-height)+2
    while True:  # page cycle
        for line_index in range(height-1):
            try:
                line = content[line_num-1 + line_index]
            except IndexError:
                line = ""
            if WINDOWS and len(line) == width:
                # avoid extra blank line by skipping linefeed print
                echo(line)
            else:
                print(line)

        callback_result = pagecallback(line_num, content_length, height)
        if callback_result == False:
            return
        elif callback_result is not None:
            line_num = callback_result

