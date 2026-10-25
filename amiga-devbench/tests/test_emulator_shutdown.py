# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Chris Collins <chris@hitorro.com>

"""A devbench's shutdown stops only an emulator that is its own child process.

Before: shutdown called stop() whenever is_running, and stop() also kills an
*external* emulator it merely found running (e.g. the QEMU behind the qemu-os4
profile), so restarting the devbench took the guest down."""
import inspect

from amiga_devbench import server
from amiga_devbench.emulator import EmulatorManager


class _Proc:
    def __init__(self, rc):
        self.returncode = rc
        self.pid = 4242


def test_owns_process_only_for_a_live_child():
    em = EmulatorManager(binary="qemu-system-ppc", process_name="qemu-system-ppc")
    assert em.owns_process is False            # nothing started (an external one may run)
    em._process = _Proc(None)
    assert em.owns_process is True             # our child, still running
    em._process = _Proc(0)
    assert em.owns_process is False            # our launcher exited: what runs now isn't ours


def test_shutdown_checks_owns_process():
    src = inspect.getsource(server)
    assert 'getattr(_emulator, "owns_process", False)' in src
    assert "if _emulator and _emulator.is_running:\n                await _emulator.stop()" not in src
