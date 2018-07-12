# TAKI

Taki is a console-based single player arcade game, acknowledged by the Taki Foundation.

It's only for Unix (Mac OS X and Linux) for now.

## Requirements
* Python 3.6
* xlib>=0.17
* pynput
### Installation

```bash
pip3 install taki
```

**If there was an error** installing pynput run:

```bash
python3 -m pip install --upgrade pip setuptools wheel
pip install xlib
pip install xlib>=0.17
pip install pynput
```

and then

```bash
pip3 install taki
```

### Game Manual

Run the command `taki` in terminal to play the game.

Press _h_ (on keyboard) to get hard and _f_ to fire. Your score is the number of chicks you've fu\**ed. You can only fu\** a chick while hard (obviously lol).

Colliding with a cactus will decrease your HP (hearts) and when it gets to zero you die!

Press esc to quit.
