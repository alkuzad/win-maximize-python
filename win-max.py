#!/usr/bin/env python

# Thanks to https://github.com/ritchielawrence/cmdow
# For providing help for treating Win32 API

import sys
import re
import os
from argparse import ArgumentParser

import win32gui
import win32api
import win32console
import win32process

class Window(object):

  def __init__(self, title):
    self.title = title
    self._handle = None
    self._find_window(title)

  def _handle_window_entry(self, hwnd, title):
    if self._handle is not None:
      return
    text = win32gui.GetWindowText(hwnd)
    if re.match(title, text) and not self._own_console(hwnd):
      self._handle = hwnd
      self._break = True

  # Check if found window handle is parent process of this script
  def _own_console(self, hwnd):
    return os.getppid() in win32process.GetWindowThreadProcessId(hwnd)

  def _find_window(self, title):
      self._handle = None
      win32gui.EnumWindows(self._handle_window_entry, '.*{}.*'.format(title))
      if self._handle is None:
        raise RuntimeError("Can not find window: {}".format(title))

  def move(self, x, y, width, height):
      win32gui.MoveWindow(self._handle, x, y, width, height, 0)

  def maximize(self):
      win32gui.ShowWindow(self._handle, 3) # SW_MAXIMIZE

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
          self.left, self.top, self.right, self.bottom = (0,0,0,0)
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
           self.monitors.append(Monitor(monitor[0].handle, index=index, rect=monitor[2]))

    def get(self, nr):
        return self.monitors[nr]

def parse_args():
    parser = ArgumentParser()
    parser.add_argument('window_title', nargs="*")
    parser.add_argument('-m', '--monitor', type=int, default=0, help="Monitor number to maximize to")
    return parser.parse_args()

def main():
    args = parse_args()
    title = ' '.join(args.window_title)
    if title == "":
        raise ValueError("No window title passed")
    monitors = MonitorCollection()
    window = Window(title)
    window.set_as_main_window_for_monitor(monitors.get(args.monitor))


if __name__ == '__main__':
  main()