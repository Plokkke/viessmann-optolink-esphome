#!/usr/bin/env bash
# Gerbers, drill, BOM and renders for ordering the heater-controller board (KiCad 10 kicad-cli).
set -euo pipefail

cd "$(dirname "$0")"
BOARD=heater-controller
OUT=fabrication

rm -rf "$OUT" && mkdir -p "$OUT/gerbers"
kicad-cli pcb drc --schematic-parity --exit-code-violations --severity-error -o "$OUT/drc.rpt" "$BOARD.kicad_pcb"
kicad-cli pcb export gerbers --layers F.Cu,B.Cu,F.Paste,F.SilkS,B.SilkS,F.Mask,B.Mask,Edge.Cuts \
  --subtract-soldermask --no-protel-ext -o "$OUT/gerbers" "$BOARD.kicad_pcb"
kicad-cli pcb export drill --format excellon --excellon-separate-th --generate-map --map-format gerberx2 \
  -o "$OUT/gerbers" "$BOARD.kicad_pcb"
(cd "$OUT/gerbers" && zip -q "../$BOARD-gerbers.zip" ./*)
kicad-cli sch export bom --fields "Reference,Value,Footprint,\${QUANTITY}" --group-by Value,Footprint \
  --exclude-dnp -o "$OUT/$BOARD-bom.csv" "$BOARD.kicad_sch"

for side in top bottom; do
  kicad-cli pcb render --side "$side" --width 1600 --height 1000 -o "$BOARD-$side.png" "$BOARD.kicad_pcb"
done
kicad-cli pcb render --perspective --rotate "-45,0,-30" --zoom 1.3 --width 1600 --height 1000 -o "$BOARD-3d.png" "$BOARD.kicad_pcb"
kicad-cli pcb export step --force -o "$BOARD.step" "$BOARD.kicad_pcb"
kicad-cli pcb export svg --mode-single --layers F.Cu,B.Cu,F.SilkS,F.Fab,Edge.Cuts --fit-page-to-board -o "$BOARD.svg" "$BOARD.kicad_pcb"
