#!/usr/bin/env bash
# Build Maze Sequencer FX: the insert-effect variant of ../vst (same sources; see ../vst/build.sh).
#   vst-fx/build/maze_seq_fx.so, vst-fx/build/skin/   one plugin folder in /sdcard/Synths (tools/release.py)
#   vst-fx/build/pluginlist-entry.xml                 the <PLUGIN ... category="Effect"> line
# Only vst.json differs ("effect": true -> PLUG_EFFECT in params.h). The skin sources are copied here
# from ../vst first, because the skin renderer's container only sees this folder.
set -euo pipefail
cd "$(dirname "$0")"
MPC_VST="${MPC_VST:-../../../mpc-vst}"
U="$(id -u):$(id -g)"
mkdir -p build
rm -rf params.json layout.conf skin.css images
cp -r ../vst/params.json ../vst/layout.conf ../vst/skin.css ../vst/images .

docker build -q -t mpc-vst-html-art "$MPC_VST/tools/html_art" >/dev/null
docker run --rm -u "$U" -e HOME=/tmp ${SHADOW_SKIN_MPC_OS:+-e SHADOW_SKIN_MPC_OS=$SHADOW_SKIN_MPC_OS} -v "$PWD":/w -v "$MPC_VST":/mv:ro -w /w mpc-vst-html-art \
  python3 /mv/tools/gen_vst.py vst.json
grep -q "PLUG_EFFECT" build/params.h || { echo "params.h has no PLUG_EFFECT: this would build the instrument"; exit 1; }
cp "$MPC_VST/wrapper/popup.h" build/

docker run --rm --platform linux/arm/v7 -v "$PWD/..":/b -w /b/vst-fx arm32v7/gcc:11-bullseye bash -euxc '
  apt-get update -qq && apt-get install -y -qq -t bullseye libasound2-dev >/dev/null
  mkdir -p build/obj
  gcc -O2 -fPIC -fvisibility=hidden -std=gnu11 -DMAZE_LFO=1 -DMAZE_VST=1 -I../src -c ../src/maze_seq_core.c -o build/obj/core.o
  g++ -O2 -fPIC -fvisibility=hidden -std=c++17 -Wall -Wextra -Wno-unused-parameter \
      -I../src -Ibuild -c ../vst/maze_seq_vst.cpp -o build/obj/vst.o
  g++ -shared -o build/maze_seq_fx.so build/obj/core.o build/obj/vst.o \
      -static-libstdc++ -static-libgcc -Wl,--no-undefined -lasound -lpthread -lm
  strip build/maze_seq_fx.so
  echo "-- exported --"; readelf --dyn-syms -W build/maze_seq_fx.so | grep -E " GLOBAL .* [0-9]+ [A-Za-z]" | grep -v UND
  echo "-- needed --"; readelf -d build/maze_seq_fx.so | grep NEEDED
  echo "-- highest glibc (MPC OS 2.x has 2.32) --"; readelf -V build/maze_seq_fx.so | grep -o "GLIBC_[0-9.]*" | sort -uV | tail -1
  chown -R '"$U"' build
'
md5sum build/maze_seq_fx.so
