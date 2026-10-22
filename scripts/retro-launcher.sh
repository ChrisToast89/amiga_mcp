#!/bin/sh
# SPDX-License-Identifier: MIT
# Start Retro Launcher, the full-screen menu that boots the classic Amiga,
# AmigaOS 4, Atari and 3DO emulators. It lives next to this checkout in
# ../retro-launcher (override with RETRO_LAUNCHER=/path/to/retro-launcher).
# Arguments pass through, e.g. --windowed or --launch amigaos4.
here="$(cd "$(dirname "$0")/.." && pwd)"
dir="${RETRO_LAUNCHER:-$here/../retro-launcher}"
if [ ! -x "$dir/run.sh" ]; then
    echo "retro-launcher not found at $dir (set RETRO_LAUNCHER)" >&2
    exit 1
fi
exec "$dir/run.sh" "$@"
