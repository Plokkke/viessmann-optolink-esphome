#!/usr/bin/env python3
"""Split the KiCad BOM: parts JLCPCB places (those in the CPL) and the LCSC cart of the hand-soldered parts.

Usage: split-bom.py <bom.csv> <cpl.csv> <jlcpcb-bom.csv> <lcsc-cart.csv>
"""
import csv
import sys

# Bought with the board but not drawn on it: the fuse that goes into the F1 holder
EXTRA_PARTS = [{"LCSC Part #": "C142808", "Quantity": "1", "Comment": "F1 fuse TR5 T1A 250V (Littelfuse 37211000001)"}]


def read(path):
    with open(path, newline="") as f:
        return list(csv.DictReader(f))


def write(path, fields, rows):
    with open(path, "w", newline="") as f:
        writer = csv.DictWriter(f, fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def main(bom_path, cpl_path, jlcpcb_path, lcsc_path):
    bom = [row for row in read(bom_path) if row["LCSC Part #"]]
    placed = {row["Designator"] for row in read(cpl_path)}
    assembled = [row for row in bom if set(row["Designator"].split(",")) <= placed]
    hand_soldered = [row for row in bom if row not in assembled]
    write(jlcpcb_path, ["Comment", "Designator", "Footprint", "LCSC Part #"], assembled)
    write(lcsc_path, ["LCSC Part #", "Quantity", "Comment"], hand_soldered + EXTRA_PARTS)


if __name__ == "__main__":
    main(*sys.argv[1:5])
