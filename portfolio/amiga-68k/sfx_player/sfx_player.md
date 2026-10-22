# SFX Player
**Platform:** Classic Amiga (68k, AGA A1200/A4000 class) · **Source:** `examples/sfx_player/` · **Type:** tool

A sound-effect player that generates sine, square, sawtooth or noise waveforms (256 samples) in chip RAM and plays them on a Paula channel through audio.device. Over the bridge (`sfx_player`) it exposes `waveform`, `frequency`, `volume`, `channel` and `playing`, a `waveform_data` memory region holding the sample, and hooks `play`, `stop`, `sweep` (from/to Hz) and `noise`.

## Running
![SFX Player window drawing a sine waveform](sfx_player.png)
Waveform Sine (0), Freq 111 Hz, Vol 64/64, Channel 0, Playing YES, Period 124, with the sine waveform drawn; captured during the bridge hook `sweep` (30 -> 111 Hz).

**Controls:** close gadget quits. **Bridge hooks:** `play`, `stop`, `sweep`, `noise`.
