#!/bin/bash
# hmp.sh 'command' ['command' ...] — send QEMU HMP monitor commands (tcp 2348) to the OS4 guest.
# e.g.  hmp.sh 'sendkey ret'   hmp.sh 'mouse_move 10 10' 'mouse_button 1' 'mouse_button 0'
for c in "$@"; do printf '%s\n' "$c"; sleep 0.15; done | nc -w 1 127.0.0.1 2348 >/dev/null
