# Bouncing Ball
**Platform:** Classic Amiga (68k, AGA A1200/A4000 class) · **Source:** `examples/bouncing_ball/` · **Type:** demo

The simplest bridge demo: a ball bouncing inside a Workbench window, with its whole state exposed for remote tweaking. It registers as `bouncing_ball` with variables `ball_x`, `ball_y`, `ball_dx`, `ball_dy`, `ball_size`, `ball_speed`, `ball_color` and `frame_count`, hooks `reset` and `status`, a custom command handler, and a `ball_state` memory region.

## Running
![Bouncing Ball window with a small blue ball](bouncing_ball.png)
The "Bouncing Ball" window on the Workbench, with the small blue rectangular "ball" in it.

**Controls:** close gadget quits. **Bridge hooks:** `reset` (re-centre the ball), `status` (position and velocity).
