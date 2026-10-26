# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Chris Collins <chris@hitorro.com>

"""A devbench's shutdown stops only an emulator that is its own.

Before: shutdown called stop() whenever is_running, and stop() also kills an
*external* emulator it merely found running (e.g. the QEMU behind the qemu-os4
profile), so restarting the devbench took the guest down."""
import asyncio

from amiga_devbench import server
from amiga_devbench.emulator import EmulatorManager
from amiga_devbench.remote_emulator import RemoteEmulatorController


class _Proc:
    """A stand-in for asyncio's Process: returncode None = still running."""

    def __init__(self, rc=None):
        self.returncode = rc
        self.pid = 4242
        self.waited = False

    async def wait(self):
        self.waited = True
        self.returncode = 0
        return 0


class _Manager(EmulatorManager):
    """Records stops instead of signalling real processes."""

    def __init__(self, external_running=False):
        super().__init__(binary="qemu-system-ppc", process_name="qemu-system-ppc")
        self.external_running = external_running
        self.external_stops = 0
        self.child_stops = 0

    @property
    def is_running(self):
        return (self._process is not None and self._process.returncode is None) or self.external_running

    async def _stop_external(self):
        self.external_stops += 1
        self.external_running = False
        return True


def _run(coro):
    return asyncio.run(coro)


def test_owns_process_only_for_a_live_child():
    em = EmulatorManager(binary="qemu-system-ppc", process_name="qemu-system-ppc")
    assert em.owns_process is False            # nothing started (an external one may run)
    em._process = _Proc(None)
    assert em.owns_process is True             # our child, still running
    em._process = _Proc(0)
    assert em.owns_process is False            # our launcher exited: what runs now isn't ours


def test_shutdown_leaves_an_adopted_emulator_running():
    em = _Manager(external_running=True)       # found running, never our child
    _run(server.shutdown_emulator(em))
    assert em.external_stops == 0
    assert em.external_running


def test_shutdown_stops_its_own_child(monkeypatch):
    em = _Manager()
    em._process = _Proc(None)
    import os
    import signal as _signal
    killed = []
    monkeypatch.setattr(os, "getpgid", lambda pid: pid)
    monkeypatch.setattr(os, "killpg", lambda pg, sig: killed.append((pg, sig)))
    _run(server.shutdown_emulator(em))
    assert killed and killed[0] == (4242, _signal.SIGTERM)
    assert em.external_stops == 0


def test_child_exiting_after_the_ownership_check_stops_nothing_else():
    """The launcher exits between owns_process and stop(): the QEMU it left must survive."""
    em = _Manager(external_running=True)
    em._process = _Proc(None)
    assert em.owns_process
    em._process.returncode = 0                 # the launcher script exits now
    _run(em.stop(owned_only=True))
    assert em.external_stops == 0
    assert em.external_running


def test_explicit_stop_still_stops_an_external_emulator():
    em = _Manager(external_running=True)
    _run(em.stop())
    assert em.external_stops == 1


def _remote():
    return RemoteEmulatorController(ssh="user@host", start_cmd="start", stop_cmd="stop")


def test_remote_emulator_found_running_is_not_stopped_at_shutdown():
    rc = _remote()
    calls = []

    async def fake_ssh(cmd, timeout=0):
        calls.append(cmd)
        return 0, "", ""

    rc._run_ssh = fake_ssh
    assert rc.owns_process is False
    _run(server.shutdown_emulator(rc))
    assert "stop" not in calls


def test_remote_emulator_we_started_is_stopped_at_shutdown(monkeypatch):
    rc = _remote()
    calls = []

    async def fake_ssh(cmd, timeout=0):
        calls.append(cmd)
        return 0, "", ""

    async def not_running(fresh=False):
        return False

    async def no_sleep(_s):
        return None

    rc._run_ssh = fake_ssh
    rc._probe_running = not_running
    monkeypatch.setattr(asyncio, "sleep", no_sleep)
    rc._started_by_us = True
    assert rc.owns_process
    _run(server.shutdown_emulator(rc))
    assert calls == ["stop"]
    assert rc.owns_process is False
