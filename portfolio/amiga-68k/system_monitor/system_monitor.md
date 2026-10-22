# System Monitor
**Platform:** Classic Amiga (68k, AGA A1200/A4000 class) · **Source:** `examples/system_monitor/` · **Type:** tool

A window showing free/total/largest chip and fast memory and the task count, exposed through the bridge as `system_monitor`: variables `frame`, `chip_free`, `fast_free`, `chip_largest`, `fast_largest`, `chip_total`, `fast_total`, `task_count`, `cpu_usage`, `update_delay`, `log_interval` and `status_msg`, hooks `snapshot` and `set_status`, a `stats` memory region, and log lines when chip memory drops or the task count changes. The CPU% figure is simulated in the source, not measured.

## Running
![System Monitor window with memory bars](system_monitor.png)
"Frame: 87 Status: running", Chip 1656360 / 2080768 and Fast 5541896 / 8388608 with bars, CPU% 5/100, Tasks 28, Chip largest 1325264 (the Fast largest line is cut off).

**Controls:** close gadget quits. **Bridge hooks:** `snapshot`, `set_status`.
