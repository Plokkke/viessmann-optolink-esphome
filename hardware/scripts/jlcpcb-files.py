#!/usr/bin/env python3
"""Order files from the KiCad BOM and placement, for the two ways of building the board:

- hand-soldered: the bare boards come from JLCPCB, every part from LCSC (LCSC cart);
- JLCPCB assembly: JLCPCB solders every part (JLCPCB BOM and CPL, no LCSC order); the fuse is bought
  separately and clipped into the F1 holder.

Usage: jlcpcb-files.py <kicad-bom.csv> <kicad-pos.csv> <lcsc-cart.csv> <jlcpcb-bom.csv> <jlcpcb-cpl.csv>
"""
import csv
import sys

BOARDS = 5  # the JLCPCB minimum: build them all

# Not drawn on the board: the fuse that clips into the F1 holder, bought with the parts when hand-soldering
LCSC_EXTRA_PARTS = [{"LCSC Part #": "C142808", "Quantity": "1",
                     "Comment": "TR5 T1A 250V time-lag fuse (Littelfuse 37211000001)"}]
# The only CPL layout JLCPCB documents as accepted (its KiCad guide): these five columns, millimetres
CPL_COLUMNS = ["Designator", "Mid X", "Mid Y", "Rotation", "Layer"]


def read(path):
    with open(path, newline="") as f:
        return list(csv.DictReader(f))


def write(path, fields, rows):
    with open(path, "w", newline="") as f:
        writer = csv.DictWriter(f, fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def cpl_row(pos):
    number = lambda value: f"{float(value):g}"
    return {"Designator": pos["Ref"], "Mid X": number(pos["PosX"]), "Mid Y": number(pos["PosY"]),
            "Rotation": number(pos["Rot"]), "Layer": pos["Side"].lower()}


def lcsc_cart(bom):
    """One line per LCSC part, quantities for every board."""
    cart = {}
    for row in bom + LCSC_EXTRA_PARTS:
        line = cart.setdefault(row["LCSC Part #"], {**row, "Quantity": 0})
        line["Quantity"] += int(row["Quantity"]) * BOARDS
    return list(cart.values())


def main(bom_path, pos_path, lcsc_path, jlcpcb_bom_path, cpl_path):
    bom = [row for row in read(bom_path) if row["LCSC Part #"]]
    placements = [cpl_row(pos) for pos in read(pos_path)]
    placed = {row["Designator"] for row in placements}
    unplaced = [row["Designator"] for row in bom if not set(row["Designator"].split(",")) <= placed]
    if unplaced:
        sys.exit(f"parts with an LCSC number but no placement: {', '.join(unplaced)}")
    write(lcsc_path, ["LCSC Part #", "Quantity", "Comment"], lcsc_cart(bom))
    write(jlcpcb_bom_path, ["Comment", "Designator", "Footprint", "LCSC Part #"], bom)
    write(cpl_path, CPL_COLUMNS, placements)


if __name__ == "__main__":
    main(*sys.argv[1:6])
