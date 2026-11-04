"""Part placements for the JLCPCB CPL, as a KiCad-style position CSV (Ref, PosX, PosY, Rot, Side).

JLCPCB places a part by its centre ("Mid X / Mid Y"), while KiCad exports the footprint origin, which is pin 1
on through-hole footprints (15 mm off on the HLK). The centre here is the middle of the part's pads.
Coordinates are in millimetres, Y up, from the page origin, like the Gerbers.

Run with KiCad's Python (pcbnew): placements.py <board.kicad_pcb> <out.csv>
"""
import csv
import sys

import pcbnew

SKIPPED = pcbnew.FP_BOARD_ONLY | pcbnew.FP_EXCLUDE_FROM_POS_FILES


def centre(footprint):
    pads = [pad.GetPosition() for pad in footprint.Pads()]
    xs, ys = [p.x for p in pads], [p.y for p in pads]
    return pcbnew.ToMM((min(xs) + max(xs)) / 2), -pcbnew.ToMM((min(ys) + max(ys)) / 2)


def rows(board):
    for footprint in sorted(board.GetFootprints(), key=lambda fp: fp.GetReference()):
        if footprint.GetAttributes() & SKIPPED or footprint.IsDNP() or not footprint.Pads():
            continue
        x, y = centre(footprint)
        yield {"Ref": footprint.GetReference(), "PosX": round(x, 4), "PosY": round(y, 4),
               "Rot": footprint.GetOrientationDegrees(), "Side": "bottom" if footprint.IsFlipped() else "top"}


def main(board_path, out_path):
    with open(out_path, "w", newline="") as f:
        writer = csv.DictWriter(f, ["Ref", "PosX", "PosY", "Rot", "Side"])
        writer.writeheader()
        writer.writerows(rows(pcbnew.LoadBoard(board_path)))


if __name__ == "__main__":
    main(*sys.argv[1:3])
