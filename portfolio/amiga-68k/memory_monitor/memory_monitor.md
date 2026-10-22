# Memory Monitor
**Platform:** Classic Amiga (68k, AGA A1200/A4000 class) · **Source:** `examples/memory_monitor/` · **Type:** tool

A memory monitor that walks Exec's `MemHeader` free lists to report free, total and largest blocks and the number of free fragments for chip and fast RAM, and graphs a history of free chip memory. Through the bridge (`memory_monitor`) it exposes those figures plus `sample_count` and `update_interval`, a `chip_samples` memory region, and hooks `snapshot`, `alloc_test` (allocate and free N bytes) and `leak_test` (deliberately leak N bytes, counted as leaks).

## Running
![Memory Monitor window with chip-free history graph](memory_monitor.png)
"Memory Monitor v1.0 [Bridge: OK]": CHIP 1617K/2031K free (largest 1294K, 8 fragments), FAST 5410K/8191K free (largest 5330K, 71 fragments), use Chip 21% / Fast 34%, 44 samples, 0 leaks, and the "Chip Free History" bar graph filling from the left. Taken just after calling the hook `alloc_test` ("alloc+free 4096 bytes. Chip delta: 0, Fast delta: 0").

**Controls:** close gadget quits. **Bridge hooks:** `snapshot`, `alloc_test`, `leak_test`.
