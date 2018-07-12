#!/usr/bin/env python3.6

import os, select
import sys
import random
import asyncio as aio
from time import sleep


import threading

from pynput.keyboard import Key, Listener
from datetime import datetime, timedelta


class _Getch:
    """Gets a single character from standard input.  Does not echo to the
screen."""
    def __init__(self):
        try:
            self.impl = _GetchWindows()
        except ImportError:
            self.impl = _GetchUnix()

    def __call__(self): return self.impl()


class _GetchUnix:
    def __init__(self):
        import tty, sys

    def __call__(self):
        import sys, tty, termios
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(sys.stdin.fileno())
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ch


class _GetchWindows:
    def __init__(self):
        import msvcrt

    def __call__(self):
        import msvcrt
        return msvcrt.getch()


class bcolors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    WARNING = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


getch = _Getch()


class Item:
    shape = [[]]
    pos = 0
    type = "NA"


class Player(Item):
    hp = 5
    state = 'NA'
    last_hard = None

    def get_hard(self):
        self.shape[4][1] = "| 0=====D"
        self.last_hard = datetime.now()
        self.state = 'H'

    def check_soft(self):
        if not self.last_hard:
            return
        dt = timedelta(seconds=3)
        if self.state == 'F':
            dt = timedelta(milliseconds=500)
        if datetime.now() - self.last_hard >= dt:
            self.state = 'NA'
            self.shape[4][1] = "|  |"

    def shoot(self):
        self.shape[4][1] = "| 0=D"
        self.last_hard = datetime.now()
        self.state = 'F'


def collide(x: Item, y: Item):
    l = min(len(x.shape), len(y.shape))
    for i in range(l):
        if not x.shape[i][1] or not y.shape[i][1]:
            continue
        l1 = x.pos + x.shape[i][0]
        r1 = l1 + len(x.shape[i][1])
        l2 = y.pos + y.shape[i][0]
        r2 = l2 + len(y.shape[i][1])
        if r1 > l2 and r2 > l1:
            return True
    return False


rows, columns = os.popen('stty size', 'r').read().split()
rows, columns = int(rows), int(columns)

score = 0


def print_line(shapes):
    st = ""
    pos = 0
    index = 0
    sbr = False
    curl = 0

    for s in shapes:
        l = s[0]
        r = ""
        while pos < l:
            r += " "
            pos += 1
        r += s[1]
        if curl + len(r) > columns:
            sbr = True
        left = columns - curl
        if sbr:
            r = r[:left]
        curl += len(r)
        for j in range(2, len(s)):
            r = s[j] + r + bcolors.ENDC
        st += r
        pos += len(s[1])
        index += 1
        if sbr:
            break
    print(st)


def print_game(p, items):
    print("_" * columns)
    sys.stdout.write(bcolors.GREEN + " score: {}   ".format(score) + bcolors.ENDC)
    sys.stdout.write(bcolors.RED)
    for j in range(p.hp):
        sys.stdout.write("\u2764 ")
    sys.stdout.write(bcolors.ENDC)
    print("                ")
    print("\n")

    for i in range(8):
        s = []
        if len(p.shape) > i:
            s.append([p.pos + p.shape[i][0], p.shape[i][1]])
            for it in items:
                if len(it.shape) > i and it.shape[i][1]:
                    si = [it.pos + it.shape[i][0], it.shape[i][1]]
                    if len(it.shape[i]) > 2:
                        si += [it.shape[i][j] for j in range(2, len(it.shape[i]))]
                    s.append(si)
        print_line(s)
    print("_" * columns)


def cactus(pos):
    i = Item()
    i.shape = [[0, ""], [0, ""], [2, "*", bcolors.GREEN], [1, "***", bcolors.GREEN], [0, "*****", bcolors.GREEN], [1, "---"], [1, "\\ /"], [2, "-"]]
    i.pos = pos
    i.type = "Cactus"
    return i


def chick(pos):
    i = Item()
    i.shape = [[1, "(**)"], [2, "||"], [1, "/  \\"], [0, "/    \\"], [1, "( ("], [1, "|  |"], [1, "|  |"], [1, "-- --"]]
    i.pos = pos
    i.type = "Chick"
    return i


frame_diff = 100 * 1000


p = Player()
P_NORM = [[1, "(oo)"], [2, "||"], [1, "/  \\"], [0, "/    \\"], [1, "|  |"], [1, "|  |"], [1, "|  |"], [1, "-- --"]]
p.shape = P_NORM
items = []

ipos = 0


def cum():
    i = Item()
    i.shape = [[0, ""], [0, ""], [0, ""], [0, ""], [0, "O"]]
    i.pos = p.shape[4][0] + len(p.shape[4][1])
    i.type = "Cum"
    return i


def last_item():
    if items:
        return items[-1]
    return p


def last_pos():
    return last_item().pos


def random_item():
    po = ipos + random.randint(1, 30)
    if not items:
        po = ipos + random.randint(20, 50)
    if random.randint(0, 1) == 0:
        return cactus(last_pos() + po - ipos), po
    else:
        return chick(last_pos() + po - ipos), po


def check_items():
    global ipos
    while len(items) < 20:
        it, po = random_item()
        if collide(last_item(), it):
            continue
        ipos = po
        items.append(it)


EXIT = False


def on_press(key):
    # print('{0} pressed'.format(
    #     key))
    global p, items, EXIT
    if EXIT:
        exit(0)
    k = str(key)
    if k == "'h'" or k == "'H'":
        p.get_hard()

    if k == "'f'" or k == "'F":
        p.shoot()
        items = [cum()] + items


def game_over():
    text = "GAME OVER!"
    while len(text) + 2 <= columns:
        text = " " + text + " "
    text = bcolors.RED + text + bcolors.ENDC
    text = bcolors.BOLD + text + bcolors.ENDC
    print(text)


def flush_input():
    while len(select.select([sys.stdin.fileno()], [], [], 0.0)[0]) > 0:
        os.read(sys.stdin.fileno(), 4096)
    game_over()
    print("press any key to exit")
    x = getch()
    return x


def on_release(key):
    global EXIT
    if EXIT:
        exit(0)
    if key == Key.esc:
        EXIT = True
        flush_input()
        exit(0)
        return False


def game():
    global items
    global p
    global P_NORM
    global score
    global ltr
    global EXIT, frame_diff

    os.system("clear")

    last_frame = datetime.now()
    check_items()
    sex = False

    FI = False
    cycle = 0

    while True:
        if EXIT:
            ltr.stop()
            exit(0)
        now = datetime.now()
        if now - last_frame >= timedelta(microseconds=frame_diff):
            last_frame = now
            if sex:
                sex = False
                if str(p.shape[4][1]).startswith("| 0====="):
                    p.shape[4][1] = "| 0=====D"
                p.shape[0][1] = "(oo)"
                items = items[1:]

            for it in items:
                if it.type == "Cum":
                    it.pos += 2
                else:
                    it.pos -= 1

            for i in range(len(items)-1):
                if items[i].type == "Cum" and collide(items[i], items[i+1]):
                    items = items[:i] + items[i+2:]
                    break

            if collide(p, items[0]):
                it = items[0]
                if it.type == "Chick":
                    if p.state == "H":
                        sex = True
                        score += 1
                        p.get_hard()
                        p.shape[4][1] = "| 0====="
                        p.shape[0][1] = "(^^)"
                        items[0].shape[4][1] = "(D ("
                        items[0].shape[0][1] = "(--)"
                    else:
                        items = items[1:]
                elif it.type == "Cactus":
                    p.hp -= 1
                    items = items[1:]
                    if p.hp == 0:
                        p.shape[0][1] = "(XX)"
                        EXIT = True
                        FI = True

        check_items()
        p.check_soft()
        clear_shell()
        print_game(p, items)
        sleep(0.05)
        if FI:
            flush_input()

        cycle += 1
        if cycle % 10000 == 0:
            frame_diff /= 2


def clear_shell():
    # os.system("clear")
    # for i in range(8):
    #     sys.stdout.write("\b" * columns)
    print('\033[H')
    for i in range(15):
        print(" " * columns)
    print('\033[H')



def listen():
    global EXIT
    with Listener(on_press=on_press, on_release=on_release) as listener:
        listener.join()
    # while True:
    #     if EXIT:
    #         exit(0)
    #     c = getch()
    #     if c == "q":
    #         EXIT = True


@aio.coroutine
def main2():
    # wait for user to press enter
    #aio.async(listen())
    game()

    # Collect events until released

    #await prompt("press enter to continue")

    # simulate raw_input
    #print(await raw_input('enter something:'))


def run():
    loop = aio.get_event_loop()
    loop.run_until_complete(main2())
    pending = aio.Task.all_tasks()
    loop.run_until_complete(aio.gather(*pending))
    loop.close()


class StoppableThread(threading.Thread):
    """Thread class with a stop() method. The thread itself has to check
    regularly for the stopped() condition."""

    def __init__(self, *args, **kwargs):
        super(StoppableThread, self).__init__(*args, **kwargs)
        self._stop_event = threading.Event()

    def start(self):
        super(StoppableThread, self).start()

    def stop(self):
        self._stop_event.set()
        #print(self.stopped())

    def stopped(self):
        return self._stop_event.is_set()


ltr = StoppableThread(target=listen, args=())


def main():
    global ltr
    ltr.start()
    run()


main()
