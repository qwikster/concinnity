import math
import time
import os
import sys
import configparser
import random
import shutil
from pathlib import Path
from queue import Queue, Empty
import threading

counters_default = ["apples", "apricots", "bananas", "blackberries", "blueberries", "cantaloupes", "cherries", "clementines", "cranberries", "currants", "dates", "grapefruit", "kiwis", "lemons", "limes", "mandarin", "mangoes", "nectarines", "oranges", "peaches", "pears", "tetopears", "pineapples", "plums", "raspberries", "strawberries", "tangerines", "watermelons"]
random.shuffle(counters_default)
increment_default = list("1234567890asdfghjkl;")
decrement_default = list("qwertyuiopzxcvbnm,./")

counter_val = []
counter_name = []
increment = []
decrement = []

key_queue = Queue(maxsize = 0)
active = True

actual_print = print
buffer = ""
listening = True

fd = None
old_settings = None

if sys.platform.startswith("win"):
    import msvcrt
    
    def listener(callback):
        while True:
            if msvcrt.kbhit():
                key = msvcrt.getch().decode("utf-8", errors = "ignore")
                callback(key)

else: # linux
    import termios
    import tty
    import select
    
    def listener(callback):
        global fd, old_settings, listening
        
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        
        try:
            tty.setcbreak(fd)
            while True:
                if listening:
                    dr, _, _ = select.select([sys.stdin], [], [], 0.05)
                    if dr:
                        key = sys.stdin.read(1)
                        callback(key)
        
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
            
def safe_input(prompt = "> "):
    global listening
    listening = False
    
    if not sys.platform.startswith("win"):
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    try:
        return input(prompt)
    finally:
        if not sys.platform.startswith("win"):
            tty.setcbreak(fd)
        listening = True
        
def on_press(key: str):
    global key_queue, active
    key_queue.put(key)

def handle_exit(exc_type, exc_value, exc_traceback):
    if exc_type is KeyboardInterrupt:
        actual_print("peace out")
    else:
        sys.__excepthook__(exc_type, exc_value, exc_traceback)

def print_buffer():
    global buffer
    actual_print(buffer, end="")
    buffer = ""

def print(*v, sep = " ", end = "\n", flush = False) -> None:
    global buffer
    buffer += sep.join(v) + end
    if flush:
        print_buffer()

def clear():
    actual_print("\033[2J\033[H", end="")

def increment_val(key):
    pass

def decrement_val(key):
    pass

def new_counter():
    global counters_default, counter_name, increment_default, decrement_default, increment, decrement, counter_val
    if len(counter_name) == 20:
        actual_print("You have all the counters we can fit on your keyboard!") # REFACTOR once i set up dynUI
        time.sleep(1)
    else:
        increment.append(increment_default[len(increment)])
        decrement.append(decrement_default[len(decrement)])
            
        counter_name.append(counters_default[len(counter_name)])
        counter_val.append(0)
        actual_print(f"{counter_name}, {increment}, {decrement}, {counter_val}")

def del_counter(key):
    global counter_name, counter_val, increment, decrement
    if key == "-":
        return
    else:
        try:
            del_key = increment.index(key)
        except ValueError:
            try:
                del_key = decrement.index(key)
            except ValueError:
                actual_print("this counter doesn't exist!") # print this inside the title bar? am i making a title bar? think about this
                time.sleep(3)
        increment.pop(del_key)
        decrement.pop(del_key)
        counter_name.pop(del_key)
        counter_val.pop(del_key)

def main():
    global active, key_queue, listener_thread
    global counter_name, increment, decrement
    
    sys.excepthook = handle_exit
    
    listener_thread = threading.Thread(target=listener, args=(on_press,), daemon=True)
    listener_thread.start()
    
    while(1):
        size_x, size_y = shutil.get_terminal_size((20, 20))
        
        if active:
            try:
                key = key_queue.get_nowait()
            except Empty:
                pass
            else:
                if key in increment:
                    increment_val(key)
                elif key in decrement:
                    decrement_val(key)
                elif key == "=":
                    new_counter()
                elif key == "-":
                    key = safe_input("press incr/decr to remove\nor '-' again to cancel\n> ")
                    del_counter(key)
                key_queue.task_done()
            
            if len(counter_name) == 0:
                random.shuffle(counters_default)
                clear()
                print("╭────────────┬────────────────────────────────────╮")
                print("│ concinnity │ no counters! press = to create one │")
                print("╰────────────┴────────────────────────────────────╯")
                print_buffer()
            
            elif len(counter_name) >= 1: # need to figure out a way to justify lines. unequal sizes of counters, maybe? an option for this?
                clear()
                longest = max(len(name) for name in counter_name)
                
                panel_width = longest + 5
                panels_wide = max(1, size_x // panel_width)
                
                for row_start in range(0, len(counter_name), panels_wide):
                    row = counter_name[row_start:row_start + panels_wide]
                    actual_print(row)
                    
                    for _ in row:
                        print("╭" + "─" * (longest + 2) + "╮ ", end = "")
                    print()
                    
                    for name in row:
                        name_padded = name.center(longest)
                        print(f"│ {name_padded} │ ", end = "")
                    print()
                    
                    for _ in row:
                        print("╞" + "═" * (longest + 2) + "╡ ", end = "")
                    print()
                    
                    for name in row:
                        find_val = counter_name.index(name)
                        print("│+│" + str(counter_val[find_val]).center(longest - 2) + "│-│ ", end = "")
                    print()
                    
                    for _ in row:
                        print("╞" + "═" * (longest + 2) + "╡ ", end = "")
                    print()
                    
                    for name in row:
                        gap = str(" ").center(longest - 4)
                        print("│- " + decrement[counter_name.index(name)] + gap + increment[counter_name.index(name)] + " +│ ", end = "")
                    print()
                    
                    for _ in row:
                        print("╰" + "─" * (longest + 2) + "╯ ", end = "")
                    print()
                    
                print_buffer()
            
            time.sleep(0.2)
                    
if __name__ == "__main__":
    main()

# [ name
# ] color 
# ` value 
# = create 
# - delete