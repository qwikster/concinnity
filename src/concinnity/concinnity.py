# TODO: add colors for just boxes, don't bother otherwise


import time
import os
import sys
import configparser
import random
import shutil
import ast
from queue import Queue, Empty
import threading

counters_default = ["apples", "apricots", "bananas", "blackberries", "blueberries", "cantaloupes", "cherries", "clementines", "cranberries", "currants", "dates", "grapefruit", "kiwis", "lemons", "limes", "mandarin", "mangoes", "nectarines", "oranges", "peaches", "pears", "tetopears", "pineapples", "plums", "raspberries", "strawberries", "tangerines", "watermelons"]
random.shuffle(counters_default)
increment_default = list("1234567890asdfghjkl;")
decrement_default = list("qwertyuiopzxcvbnm,./")
title_hint = "['] help, [\\] quit" 
title_msg = ""

counter_val = []
counter_name = []
increment = []
decrement = []

key_queue = Queue(maxsize = 0)
active = True
last_press = 0

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

class color: # \x1b[38;2;RED;GREEN;BLUEm
    NUMBER = "\x1b[38;2;20;255;220m"
    NAME = "\x1b[38;2;30;30;100m"
    BUTTON = "\x1b[38;2;200;20;200m"
    ERROR = "\x1b[38;2;255;0;100m"
    PROMPT = "\x1b[38;2;180;200;200m"
    COLOR_1 = "\x1b[38;2;9;230;169m"
    COLOR_2 = "\x1b[38;2;9;230;169m"
    COLOR_3 = "\x1b[38;2;9;230;169m"
    COLOR_4 = "\x1b[38;2;9;230;169m"
    COLOR_5 = "\x1b[38;2;9;230;169m"
    COLOR_6 = "\x1b[38;2;9;230;169m"
    COLOR_7 = "\x1b[38;2;9;230;169m"
    COLOR_8 = "\x1b[38;2;9;230;169m"
    
    RANDOM_COLOR = [COLOR_1, COLOR_2, COLOR_3, COLOR_4, COLOR_5, COLOR_6, COLOR_7, COLOR_8]

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
    global key_queue, active, last_press
    if (time.time() - last_press) < 0.1:
        return None
    last_press = float(time.time())
    key_queue.put(key)

def handle_exit(exc_type, exc_value, exc_traceback):
    global fd, old_settings, listening
    if exc_type is KeyboardInterrupt:
        actual_print("peace out")
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        sys.exit(0)
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
    global increment, counter_name, counter_val, storage, storage_path
    index = increment.index(key)
    counter_val[index] += 1
    
    storage["data"]["counter_val"] = str(counter_val)
    
    with open(storage_path, 'w', encoding = "utf-8-sig") as storagefile:
        storage.write(storagefile)

def decrement_val(key):
    global increment, counter_name, counter_val, storage, storage_path
    index = decrement.index(key)
    counter_val[index] -= 1
    
    storage["data"]["counter_val"] = str(counter_val)
    
    with open(storage_path, 'w', encoding = "utf-8-sig") as storagefile:
        storage.write(storagefile)

def new_counter():
    global counters_default, counter_name, increment_default, decrement_default, increment, decrement, counter_val, storage, storage_path
    if len(counter_name) == 20:
        actual_print("you have all the counters\nwe can fit on your keyboard!")
        time.sleep(1)
    else:
        increment.append(increment_default[len(increment)])
        decrement.append(decrement_default[len(decrement)])
        
        counter_name.append(counters_default[len(counter_name)])
        counter_val.append(0)
            
        storage["data"]["counter_name"] = str(counter_name)
        storage["data"]["counter_val"] = str(counter_val)
        storage["data"]["increment"] = str(increment)
        storage["data"]["decrement"] = str(decrement)

        with open(storage_path, 'w', encoding = "utf-8-sig") as storagefile:
            storage.write(storagefile)

def del_counter(key):
    global counter_name, counter_val, increment, decrement, title_msg
    if key == "-":
        return
    else:
        try:
            del_key = increment.index(key)
        except ValueError:
            try:
                del_key = decrement.index(key)
            except ValueError:
                actual_print("this counter doesn't exist!")
                time.sleep(3)
                return
            
        increment.pop(len(increment) - 1)
        decrement.pop(len(decrement) - 1)
        counter_name.pop(del_key)
        counter_val.pop(del_key)
        
        storage["data"]["counter_name"] = str(counter_name)
        storage["data"]["counter_val"] = str(counter_val)
        storage["data"]["increment"] = str(increment)
        storage["data"]["decrement"] = str(decrement)
        
        with open(storage_path, 'w', encoding = "utf-8-sig") as storagefile:
            storage.write(storagefile)

def set_value(key, num):
    global counter_val, increment, decrement, storage, storage_path
    if key == "`" or key == "~":
        return
    else:
        try:
            mod_key = increment.index(key)
        except ValueError:
            try:
                mod_key = decrement.index(key)
            except ValueError:
                actual_print("this counter doesn't exist!")
                time.sleep(3)
                return

        counter_val[mod_key] = num
        storage["data"]["counter_val"] = str(counter_val)
        with open(storage_path, 'w', encoding = "utf-8-sig") as storagefile:
            storage.write(storagefile)
            
def set_name(key, name):
    global counter_name, increment, decrement, storage, storage_path
    if key == "[" or key == "{":
        return
    else:
        try:
            mod_key = increment.index(key)
        except ValueError:
            try:
                mod_key = decrement.index(key)
            except ValueError:
                actual_print("this counter doesn't exist!")
                time.sleep(3)
                return
        try:
            counter_name[mod_key] = name
            storage["data"]["counter_name"] = str(counter_name)
        except Exception:
            actual_print("invalid name! special chars?")
            time.sleep(2)
        with open(storage_path, 'w', encoding = "utf-8-sig") as storagefile:
            storage.write(storagefile)

def load_storage(storage, storage_path):
    global counter_val, counter_name, increment, decrement, increment_default, decrement_default, title_hint, counters_default
    
    counters_default = ast.literal_eval(storage["data"]["counters_default"])
    increment_default = ast.literal_eval(storage["data"]["increment_default"])
    decrement_default = ast.literal_eval(storage["data"]["decrement_default"])
    counter_name = ast.literal_eval(storage["data"]["counter_name"])
    counter_val = ast.literal_eval(storage["data"]["counter_val"])
    increment = ast.literal_eval(storage["data"]["increment"])
    decrement = ast.literal_eval(storage["data"]["decrement"])
    title_hint = storage["data"]["title_hint"]

def help_menu():
    size_x, size_y = shutil.get_terminal_size((20, 20))
    
    clear()
    print("┏" + "━" * (size_x - 3) + "┓")
    print(f"┃ concinnity: {"help".ljust(size_x - 16)}┃")
    print("┠───┬" + "─" * (size_x - 7) + "┨")
    print(f"┃=/+│ {" Create a new counter".ljust(size_x - 8)}┃")
    print(f"┃ - │ {" Delete a counter".ljust(size_x - 8)}┃")
    print(f"┃ [ │ {" Edit a name".ljust(size_x - 8)}┃")
    print(f"┃~/`│ {" Manually choose value".ljust(size_x - 8)}┃")
    print("┠───┴" + "─" * (size_x - 7) + "┨")
    print("┃" + " Hit [ENTER] to return".ljust(size_x - 3) + "┃")
    print("┗" + "━" * (size_x - 3) + "┛")
    
    print_buffer()
    input("")

def main():
    global active, key_queue, listener_thread, title_msg, title_hint
    global counter_name, increment, decrement, counter_val
    global theme, storage, theme_path, storage_path
    
    sys.excepthook = handle_exit
    
    listener_thread = threading.Thread(target=listener, args=(on_press,), daemon=True)
    listener_thread.start()
     
    try:
        theme = configparser.ConfigParser()
        theme_path = f"{os.path.dirname(os.path.abspath(__file__))}/concinnity.cfg"
        theme.read(theme_path, encoding = "utf-8-sig")
        
    except Exception: 
        actual_print("Could not read your theme file.\nMake sure you got this file\nfrom PyPi, not GitHub! This file\nis required to function.\n\n(cd/concinnity.cfg)")
        sys.exit(0)
        
    if os.path.exists(f"{os.path.dirname(os.path.abspath(__file__))}/concinnity.data"):
        storage = configparser.ConfigParser()
        storage_path = f"{os.path.dirname(os.path.abspath(__file__))}/concinnity.data"
        storage.read(storage_path, encoding = "utf-8-sig")
    
    else:
        storage = configparser.ConfigParser()
        
        storage["data"] = {}
        storage["data"]["counters_default"] = str(counters_default)
        storage["data"]["increment_default"] = str(increment_default)
        storage["data"]["decrement_default"] = str(decrement_default)
        storage["data"]["title_hint"] = str(title_hint)
        storage["data"]["counter_name"] = str(counter_name)
        storage["data"]["counter_val"] = str(counter_val)
        storage["data"]["increment"] = str(increment)
        storage["data"]["decrement"] = str(decrement)
        
        storage_path = f"{os.path.dirname(os.path.abspath(__file__))}/concinnity.data"
        
        with open(storage_path, 'w', encoding = "utf-8-sig") as storagefile:
            storage.write(storagefile)
            
        storage.read(storage_path, encoding = "utf-8-sig")
        
    load_storage(storage, storage_path)
    
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
                elif key == "=" or key == "+":
                    new_counter()
                elif key == "-" or key == "_":
                    key = safe_input("press incr/decr of a counter\nto delete it, or '-'\nagain to cancel:\n\n> ")
                    del_counter(key)
                elif key == "'":
                    active = False
                    help_menu()
                    active = True
                elif key == "\\" or key == "|":
                    global fd, old_settings, listening
                    termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
                    sys.exit(0)
                elif key == "`" or key == "~":
                    key = safe_input("press incr/decr of a counter\nto change its value,\nor ~ / ` again to cancel:\n\n> ")
                    while(1):
                        try:
                            num = safe_input("enter value:\n\n> ")
                            num = int(num)
                            break
                        except ValueError:
                            print("this is not a number!")
                            pass
                    set_value(key, num)
                elif key == "[" or key == "{":
                    key = safe_input("press incr/decr of a counter\nto change its name,\nor '[' again to cancel:\n\n> ")
                    name = safe_input("enter name:\n\n> ")
                    set_name(key, name)
                key_queue.task_done()
            
            if len(counter_name) >= 1:
                clear()
                title_msg = ""
                i = 0

                while i < len(counter_name):
                    line_boxes = []
                    used_width = 0
                    min_width = 8

                    while i < len(counter_name):
                        name = counter_name[i]
                        val = str(counter_val[i])
                        inc = increment[i]
                        dec = decrement[i]
                        
                        if (len(val) % 2) != (len(name) % 2):
                            val = val.zfill(len(val) + 1)

                        if len(name) % 2 == 0:
                            min_width = 8
                        else:
                            min_width = 7
                        
                        inner_width = max(len(name), len(f"-- {val} --"), min_width)
                        box_width = inner_width + 4
                        
                        if used_width + box_width > size_x:
                            break
                        
                        top = "╭" + "─" * (inner_width + 2) + "╮"
                        name_l = f"│ {name.center(inner_width)} │"
                        val_l = f"│ -║ {val.center(inner_width - 6)} ║+ │"
                        keys_l = f"╰─[{dec}]{'─' * (inner_width - 6)}[{inc}]─╯"
                        separator_top = f"╞══╦{"═" * (inner_width - 4)}╦══╡"
                        separator_bottom = f"╞══╩{"═" * (inner_width - 4)}╩══╡"

                        line_boxes.append((top, name_l, separator_top, val_l, separator_bottom, keys_l))
                        used_width += box_width + 1
                        i += 1
                        
                    for row in zip(*line_boxes):
                        print(" ".join(row))
                
            elif len(counter_name) == 0:
                    title_msg = "no counters! press ="
                    random.shuffle(counters_default)

            if len(title_msg) == 0:
                title = title_hint
            else:
                title = title_msg

            print("┏" + "━" * (size_x - 3) + "┓")
            print(f"┃ concinnity: {title.ljust(size_x - 16)}┃")
            print("┗" + "━" * (size_x - 3) + "┛")
            
            clear()
            print_buffer()
            
            time.sleep(0.1)
                    
if __name__ == "__main__":
    main()