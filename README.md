# concinnity
clean and aesthetic CLI counter tool!
> harmony or elegance of design in adaptation of parts to a whole or to each other

## features
- easy to use theme management and configuration!
- runs on any machine
- support for up to 20 counters consecutively! increment or decrement with your keyboard
- adaptive based on your terminal size and shape!
- press `=` (the plus key) to create a new counter instantly
- press the `[` key then any increment or decrement key to edit the name or any counter (i recommend you use short names)
- use `'` to manually input the value of any counter
- `-` will delete a counter
- saves all content automatically!

## installation
`pip install concinnity`, or if you're on certain flavors of linux (it'll tell you) `pipx install concinnity`.\
please don't install from github!\
arch: `sudo pacman -S python-pipx` to get that tool

## usage
you can run the command `concinnity`, but i will admit it's a pain to memorize...\
feel free to type `counter` instead :)

## config
you may customize the default names or keys for new counters in the project's folder. on linux, using pipx:
`~/.local/share/pipx/venvs/concinnity/lib/python3.13/site-packages/concinnity/concinnity.data`
i'm not sure where you'll find the project on other platforms, sorrie

## credit
certain amounts of code from my other project [hackaclime](https://github.com/qwikster/hackaCLIme/) was reused in this project.

i ran out of time to add theme support; maybe i'll revisit this in the future.