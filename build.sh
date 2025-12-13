#!/bin/bash

rm -rf build dist
mkdir -p bin

pyinstaller --noconsole --onefile --windowed \
  --icon=icon/icon.png \
  --add-data "Config/config_cube16l.json:Config" \
  --add-data "Guider/hall_array.ui:Guider" \
  --add-data "ImageJig/CUBE_Zig.png:ImageJig" \
  hall_array_viewer.py --distpath bin 

echo "1.Build done"
