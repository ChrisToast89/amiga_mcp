# Disk Benchmark
**Platform:** Classic Amiga (68k, AGA A1200/A4000 class) · **Source:** `examples/disk_benchmark/` · **Type:** tool

A file-system throughput benchmark: it writes and then reads back a test file at a chosen path with dos.library `Write`/`Read`, timing with `DateStamp`, and shows the speeds as bars. Over the bridge (`disk_benchmark`) it exposes `test_path`, `block_size`, `test_size`, `read_speed`, `write_speed` and `status_msg`, a `results` memory region, and hooks `run_read`, `run_write`, `run_all` and `set_path`.

## Results
![Disk Benchmark window showing RAM: results](disk_benchmark.png)
After the bridge hook `run_all` on `RAM:`: "Done: W=3200 R=3200 KB/s", block 4096, size 65536 bytes, write and read bars at 3200 KB/s (3276800 B/s each), R/W ratio 1.00.

**Controls:** Path field and Write / Read / Both buttons; close gadget quits. **Bridge hooks:** `run_read`, `run_write`, `run_all`, `set_path`.
