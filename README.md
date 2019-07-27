# Win Maximize (Windows only)

Finds Windows window by name (or part of it, or regex) and moves to monitor specified by monitor number or to monitor where mouse cursor is placed. Window is also maximized and placed on top. 

Automatically detects if found window is part of current process tree (as command line will have same text).

I'm using it when I work on multiple Sublime Text 3 projects and I want to switch between them easily without alt-tabbing. I've done that by monkey-patching GotoWindow plugin.

I've written is as replacement for https://github.com/ritchielawrence/cmdow which is excellent but antyvirus programs detects it as malware (which it is not but ...). If you do not have agressive corporate AV installed then I suggest just using it.


# Installation

Install via pip: `pip install win-maximize`

# Usage

```
usage: win-mazimize [-h] [-m MONITOR] [-c] [window_title [window_title ...]]

positional arguments:
  window_title

optional arguments:
  -h, --help            show this help message and exit
  -m MONITOR, --monitor MONITOR
                        Monitor number to maximize to (if you have only 1
                        monitor - pass 0)
  -c, --cursor-track    Move window to monitor where cursor is located
```

