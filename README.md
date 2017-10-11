# What it does ?
Move window to designed monitor number + maximize. I've written is as poor man replacement for
https://github.com/ritchielawrence/cmdow which is detected as malware via most antyvirus programs (due to 
window hiding abilities).

# Dependencies

win32api libraries, can be installed via pip: `pip install pypiwin32`

# Using

```
usage: win-max.py [-h] [-m MONITOR] [window_title [window_title ...]]

positional arguments:
  window_title

optional arguments:
  -h, --help            show this help message and exit
  -m MONITOR, --monitor MONITOR
                        Monitor number to maximize to
```
