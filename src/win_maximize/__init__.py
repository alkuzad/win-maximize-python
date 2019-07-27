#!/usr/bin/env python

# Thanks to https://github.com/ritchielawrence/cmdow
# For providing help for treating Win32 API

import re
import os
from argparse import ArgumentParser

import win32gui
import win32api
import win32console
import win32process

from win32com.client import GetObject

from win_maximize.parent_tree import parent_tree


def mouse_position():
    _flags, _handle, pos = win32gui.GetCursorInfo()
    return pos


CURRENT_PROCESS_TREE = parent_tree(os.getpid())


class Window(object):
    def __init__(self, title):
        self.title = title
        self._matcher = re.compile(f'.*{title}.*')
        self._handle = None
        self._find_window(title)

    def _handle_window_entry(self, hwnd, _):
        if self._handle is not None:
            raise StopIteration
        if not self._own_console(hwnd):
            text = win32gui.GetWindowText(hwnd)
            if self._matcher.match(text):
                self._handle = hwnd

    # Check if found window handle is parent process of this script
    def _own_console(self, hwnd):
        return any(
            [
                x in CURRENT_PROCESS_TREE
                for x in win32process.GetWindowThreadProcessId(hwnd)
            ]
        )

    def _find_window(self, title):
        self._handle = None
        try:
            win32gui.EnumWindows(self._handle_window_entry, None)
        except StopIteration:
            pass
        if self._handle is None:
            raise RuntimeError("Can not find window: {}".format(title))

    def move(self, x, y, width, height):
        win32gui.MoveWindow(self._handle, x, y, width, height, 0)

    def maximize(self):
        win32gui.ShowWindow(self._handle, 3)  # SW_MAXIMIZE

    def foreground(self):
        res = win32gui.SystemParametersInfo(0x2000, 0, 0x0000)
        if res:
            win32gui.SetForegroundWindow(win32console.GetConsoleWindow())
        win32gui.SetForegroundWindow(self._handle)

    def set_as_main_window_for_monitor(self, monitor):
        self.move(monitor.left, monitor.top, monitor.width, monitor.height)
        self.maximize()
        self.foreground()


class Monitor(object):
    def __init__(self, handle, index=None, rect=None):
        self._handle = handle
        if rect is None:
            self.left, self.top, self.right, self.bottom = (0, 0, 0, 0)
        else:
            self.left, self.top, self.right, self.bottom = rect
        self.index = index

    @property
    def width(self):
        return abs(self.left - self.right)

    @property
    def height(self):
        return abs(self.bottom - self.top)


class MonitorCollection(object):
    def __init__(self):
        self.monitors = []
        self._find_monitors()

    def _find_monitors(self):
        for index, monitor in enumerate(win32api.EnumDisplayMonitors()):
            self.monitors.append(
                Monitor(monitor[0].handle, index=index, rect=monitor[2])
            )

    def get(self, nr):
        return self.monitors[nr]

    def monitor_with_cursor(self):
        mouse_x, mouse_y = mouse_position()
        for monitor in self.monitors:
            if (
                mouse_x >= monitor.left
                and mouse_x <= monitor.right
                and mouse_y >= monitor.top
                and mouse_y <= monitor.bottom
            ):
                return monitor


def parse_args():
    parser = ArgumentParser()
    parser.add_argument(
        "window_title",
        nargs="+",
        help="Window title to catch, does not need to be quoted",
    )
    parser.add_argument(
        "-m",
        "--monitor",
        type=int,
        help="Monitor number to maximize to (if you have only 1 monitor - pass 0)",
    )
    parser.add_argument(
        "-c",
        "--cursor-track",
        action="store_true",
        default=False,
        help="Move window to monitor where mouse cursor is located",
    )
    return parser.parse_args()


def main():
    args = parse_args()

    title = " ".join(args.window_title)

    monitors = MonitorCollection()
    window = Window(title)

    if args.monitor is not None:
        window.set_as_main_window_for_monitor(monitors.get(args.monitor))
    elif args.cursor_track:
        window.set_as_main_window_for_monitor(monitors.monitor_with_cursor())
    else:
        raise RuntimeError("Either window number or --cursor-track has to be passed")


if __name__ == "__main__":
    main()
