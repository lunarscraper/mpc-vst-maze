# Vendored: maze_seq_core.c / maze_seq_host.h

Source: `sd88me/force-maze`, `maze-sequencer/src/maze_seq_core.c` + `maze_seq_host.h`
Vendored at commit: `abae5ea` (2026-10-02). License: MIT (same author, see `LICENSE`).

The core is `schwung-maze`'s `maze_seq.c` as already adapted for the Force (MockbaMod) build. It is vendored here so this
port stays self-contained. Local changes, all behind `#ifdef MAZE_VST` (the build defines it; the other builds are
unchanged) and marked `MPC-VST-ONLY`:

1. **No state file, no worker thread.** The Force build keeps one `maze_seq.bin` per process; with several plugin
   instances in several projects that would be shared and wrong. The project chunk carries the state instead.
2. **`pattern`** (`get_param` / `set_param`): the step bits and CV values of both lines as
   `<8 bits>:<8 cv>|<8 bits>:<8 cv>`, so a saved project replays the exact pattern (the core's `get_param` does not
   expose CV).
3. **`s1_regen` / `s2_regen`**: re-roll one line's pattern (keeps its length, channel, corrupt, range and reset).
4. **`host_bpm`**: tempo for LFO sync. The core estimates tempo from the wall-clock gap between clock pulses, which is
   meaningless in a plugin where pulses arrive in a burst per audio block.

5. **`s1_adv` / `s2_adv`**: rotate that line's pattern (gates and CV of its active steps) one step forward per press,
   also while stopped. The Force build's version only moves the play-head, which is inaudible when stopped.

6. **`host_pulse`** (`set_param`): sets the pulse counter, so the wrapper can make it the absolute 24-PPQN index of
   the host position (`ppqPos * 24`). Steps fire on `pulse % RATE_PULSES == 0`, so they then sit ON the MPC grid:
   the first step on the downbeat, and still on the grid after a locate or a note-rate change. Without it the core
   counts from the Start message, which put every step off the grid in a plugin (see `maze_seq_vst.cpp`, PpqClock).

Re-vendor by diffing against force-maze's `src/` at a newer commit and re-applying these six.
