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

Re-vendor by diffing against force-maze's `src/` at a newer commit and re-applying these four.
