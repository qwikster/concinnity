import math
import time
import os
import sys
import configparser
import random
import shutil
from pathlib import Path
from queue import Queue, Empty

from pynput import keyboard
from pynput.keyboard import KeyCode

counters_default = ["apples", "apricots", "bananas", "blackberries", "blueberries", "cantaloupes", "cherries", "clementines", "cranberries", "currants", "dates", "figs", "grapefruit", "kiwi", "lemons", "limes", "mandarin", "mangoes", "nectarines", "oranges", "peaches", "pears", "tetopears", "pineapples", "plums", "raspberries", "strawberries", "tangerines", "watermelons"]
increment_default = list("1234567890asdfghjkl;")
decrement_default = list("qwertyuiopzxcvbnm,./")

counter_name = []
increment = []
decrement = []

key_queue = Queue(maxsize = 0)
active = True

actual_print = print
buffer = ""

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
    global counters_default, counter_name, increment_default, decrement_default, increment, decrement
    if len(counter_name) == 20:
        actual_print("You have all the counters we can fit on your keyboard!") # REFACTOR once i set up dynUI
    else:
        increment.append(increment_default[len(increment)])
        decrement.append(decrement_default[len(decrement)])
        counter_name.append(random.choice(counters_default))
        actual_print(f"{counter_name}, {increment}, {decrement}")

def on_release(key):
    global increment
    global decrement
    global key_queue
    try:
        key_queue.put(key.char)
    except AttributeError:
        actual_print("special key pressed") #debug

def main():
    global active, key_queue
    global counter_name, increment, decrement
    listener = keyboard.Listener(on_release = on_release)
    listener.start()

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
                    actual_print("yeppers")
                    new_counter()
                key_queue.task_done()
            
            if len(counter_name) == 0:
                clear()
                print("╭────────────┬────────────────────────────────────╮")
                print("│ concinnity │ no counters! press = to create one │")
                print("╰────────────┴────────────────────────────────────╯")
                print_buffer()
            
            elif len(counter_name) >= 1:
                clear()
                longest = 0
                for i in range(len(counter_name)):
                    if len(counter_name[i]) > longest:
                        longname = counter_name[i]
                        longest = len(counter_name[i])
                        
                for i in range(size_x // (longest + 5)): # LEFT OFF HERE: need to figure out how to split longest + 5 into rows based on how large the boxes will be
                    print("╭", end = "")
                    for j in range(longest + 2):
                        print("─", end = "")
                    print("╮ ", end = "")
                print("\n")
                print_buffer()
                
            time.sleep(0.5)
                    
if __name__ == "__main__":
    main()

# [ name
# ] color 
# ` value 
# = create 
# - delete