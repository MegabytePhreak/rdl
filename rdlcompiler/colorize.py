__author__ = 'megabytephreak'

import sys

try:
    import colorama
    color_enabled = True
    RED = colorama.Fore.RED #+ colorama.Style.BRIGHT
    BOLD = colorama.Style.BRIGHT

except ImportError:
    color_enabled = False
    RED = ""
    BOLD = ""


def init(enable=True, out=sys.stderr):
    global color_enabled
    color_enabled = enable and color_enabled and out.isatty()

    if color_enabled:
        colorama.init()


def colorize(color, text):

    if color_enabled:
        return color + text + colorama.Fore.RESET + colorama.Style.NORMAL

    return text


