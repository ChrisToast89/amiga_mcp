# hello
**Platform:** 3DO Interactive Multiplayer (ARM60, Portfolio OS; Opera emulator) · **Source:** `3do_dev/projects/hello/` · **Type:** demo

The starter program every new project is created from (`./3do new` copies it from `sdk/template`): a double-buffered display, controller input and debug logging. Its `test.py` checks for the `hello: ready` log line and takes one screenshot. Native framebuffer 320x240, shown here at 3x (960x720, nearest-neighbour).

## Running
![hello running in the emulator](hello.png)
A dark-blue screen with "HELLO" and a frame counter ("FRAME 41") at top left and "HELLO 3DO" in the centre.

**Controls:** D-pad and buttons are read and logged · X: quit
