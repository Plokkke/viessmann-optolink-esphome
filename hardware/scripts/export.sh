#!/usr/bin/env bash
# Everything generated from the heater-controller KiCad project (KiCad 10 kicad-cli):
#   fabrication/  Gerbers and drill, plus the order files of both builds (not versioned):
#                 hand-soldered/ (LCSC cart) and jlcpcb-assembly/ (JLCPCB BOM and CPL)
#   exports/      renders, schematic and 1:1 board plots, STEP and STL models for the enclosure
set -euo pipefail

cd "$(dirname "$0")/.."
BOARD=heater-controller
FAB=fabrication
EXPORTS=exports
KICAD_PYTHON=${KICAD_PYTHON:-/Applications/KiCad/KiCad.app/Contents/Frameworks/Python.framework/Versions/Current/bin/python3}

rm -rf "$FAB" && mkdir -p "$FAB/gerbers" "$FAB/hand-soldered" "$FAB/jlcpcb-assembly" "$EXPORTS"
kicad-cli pcb drc --schematic-parity --exit-code-violations --severity-error -o "$FAB/drc.rpt" "$BOARD.kicad_pcb"
kicad-cli pcb export gerbers --layers F.Cu,B.Cu,F.Paste,F.SilkS,B.SilkS,F.Mask,B.Mask,Edge.Cuts \
  --subtract-soldermask --no-protel-ext -o "$FAB/gerbers" "$BOARD.kicad_pcb"
kicad-cli pcb export drill --format excellon --excellon-separate-th --generate-map --map-format gerberx2 \
  -o "$FAB/gerbers" "$BOARD.kicad_pcb"
(cd "$FAB/gerbers" && zip -q "../$BOARD-gerbers.zip" ./*)
BOM=$(mktemp) POS=$(mktemp)
kicad-cli sch export bom --fields 'Value,Reference,Footprint,LCSC,${QUANTITY}' \
  --labels "Comment,Designator,Footprint,LCSC Part #,Quantity" --group-by "LCSC,Value,Footprint" \
  --ref-range-delimiter "" --exclude-dnp -o "$BOM" "$BOARD.kicad_sch"
"$KICAD_PYTHON" scripts/placements.py "$BOARD.kicad_pcb" "$POS"
scripts/jlcpcb-files.py "$BOM" "$POS" "$FAB/hand-soldered/$BOARD-lcsc-cart.csv" \
  "$FAB/jlcpcb-assembly/$BOARD-bom.csv" "$FAB/jlcpcb-assembly/$BOARD-cpl.csv"
rm "$BOM" "$POS"

for side in top bottom; do
  kicad-cli pcb render --side "$side" --width 1600 --height 1000 -o "$EXPORTS/$BOARD-$side.png" "$BOARD.kicad_pcb"
done
kicad-cli pcb render --perspective --rotate "-45,0,-30" --zoom 1.3 --width 1600 --height 1000 -o "$EXPORTS/$BOARD-3d.png" "$BOARD.kicad_pcb"
for format in step stl; do
  kicad-cli pcb export "$format" --force -o "$EXPORTS/$BOARD.$format" "$BOARD.kicad_pcb"
done
# 1:1 print of the board, to check the parts on paper
kicad-cli pcb export svg --mode-single --layers F.Cu,B.Cu,F.SilkS,F.Fab,Edge.Cuts --fit-page-to-board \
  -o "$EXPORTS/$BOARD-pcb.svg" "$BOARD.kicad_pcb"
SCH_SVG=$(mktemp -d)
kicad-cli sch export svg -o "$SCH_SVG" "$BOARD.kicad_sch"
mv "$SCH_SVG/$BOARD.svg" "$EXPORTS/$BOARD-schematic.svg" && rmdir "$SCH_SVG"
