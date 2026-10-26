#!/usr/bin/env python3
"""ESP32-C3 super mini footprint, module plugged into two 1x8 SMD female sockets (staggered legs)."""
import sys
import uuid

# Measured on the module (USB end at the top, -y, components visible)
WIDTH = 18.0
LENGTH = 22.0
USB_OVERHANG = 1.5
USB_WIDTH = 9.0
ROW_SPACING = (13.8 + 18.0) / 2
PITCH = 2.54
FIRST_PIN_FROM_USB_EDGE = PITCH / 2
# SMD socket strip: legs alternate on each side of the row
LEG_OFFSET = 1.65
PAD_SIZE = (1.9, 1.0)
SOCKET_HALF_WIDTH = 1.27
ANTENNA_KEEPOUT = 2.3
KEEPOUT_HALF_WIDTH = ROW_SPACING / 2 - LEG_OFFSET - 1.2

# Pins 1-8 on the right (5V GND 3V3 GPIO4..0), 9-16 on the left (GPIO5..10 GPIO20 GPIO21), USB end first
RIGHT_PINS = range(1, 9)
LEFT_PINS = range(9, 17)


def u():
    return str(uuid.uuid4())


def pin_y(index):
    return round(-LENGTH / 2 + FIRST_PIN_FROM_USB_EDGE + index * PITCH, 3)


def pad(number, side, index):
    stagger = LEG_OFFSET if index % 2 == 0 else -LEG_OFFSET
    x = round(side * (ROW_SPACING / 2 - stagger), 3)
    return (f'\t(pad "{number}" smd roundrect\n\t\t(at {x} {pin_y(index)})\n'
            f"\t\t(size {PAD_SIZE[0]} {PAD_SIZE[1]})\n"
            '\t\t(layers "F.Cu" "F.Mask" "F.Paste")\n\t\t(roundrect_rratio 0.25)\n'
            f'\t\t(uuid "{u()}")\n\t)')


def stroke(width):
    return f"\t\t(stroke\n\t\t\t(width {width})\n\t\t\t(type solid)\n\t\t)"


def rect(layer, x0, y0, x1, y1, width):
    return (f"\t(fp_rect\n\t\t(start {x0} {y0})\n\t\t(end {x1} {y1})\n{stroke(width)}\n\t\t(fill no)\n"
            f'\t\t(layer "{layer}")\n\t\t(uuid "{u()}")\n\t)')


def label(value, y, layer="F.Fab", kind=None):
    head = f'\t(property "{kind}" "{value}"' if kind else f'\t(fp_text user "{value}"'
    return (f'{head}\n\t\t(at 0 {y} 0)\n\t\t(layer "{layer}")\n\t\t(uuid "{u()}")\n'
            "\t\t(effects\n\t\t\t(font\n\t\t\t\t(size 1 1)\n\t\t\t\t(thickness 0.15)\n\t\t\t)\n\t\t)\n\t)")


def socket_model(side):
    """KiCad SMD socket model, centred on the strip; pin 1 leg sits on the inner side of each row."""
    variant = "Pin1Left" if side > 0 else "Pin1Right"
    centre_y = (pin_y(0) + pin_y(7)) / 2
    return (f'\t(model "${{KICAD10_3DMODEL_DIR}}/Connector_PinSocket_2.54mm.3dshapes/'
            f'PinSocket_1x08_P2.54mm_Vertical_SMD_{variant}.step"\n'
            f"\t\t(offset\n\t\t\t(xyz {side * ROW_SPACING / 2} {round(-centre_y, 3)} 0)\n\t\t)\n"
            "\t\t(scale\n\t\t\t(xyz 1 1 1)\n\t\t)\n\t\t(rotate\n\t\t\t(xyz 0 0 0)\n\t\t)\n\t)")


def antenna_keepout():
    top = LENGTH / 2 - ANTENNA_KEEPOUT
    xy = " ".join(f"(xy {x} {y})" for x, y in (
        (-KEEPOUT_HALF_WIDTH, top), (KEEPOUT_HALF_WIDTH, top),
        (KEEPOUT_HALF_WIDTH, LENGTH / 2), (-KEEPOUT_HALF_WIDTH, LENGTH / 2)))
    return ('\t(zone\n\t\t(net 0)\n\t\t(net_name "")\n\t\t(layers "F.Cu" "B.Cu")\n'
            f'\t\t(uuid "{u()}")\n\t\t(name "antenna_keepout")\n\t\t(hatch edge 0.5)\n'
            "\t\t(connect_pads\n\t\t\t(clearance 0)\n\t\t)\n\t\t(min_thickness 0.25)\n"
            "\t\t(filled_areas_thickness no)\n\t\t(keepout\n\t\t\t(tracks not_allowed)\n"
            "\t\t\t(vias not_allowed)\n\t\t\t(pads not_allowed)\n\t\t\t(copperpour not_allowed)\n"
            "\t\t\t(footprints allowed)\n\t\t)\n\t\t(placement\n\t\t\t(enabled no)\n"
            "\t\t\t(sheetname \"\")\n\t\t)\n\t\t(fill\n\t\t\t(thermal_gap 0.5)\n"
            f"\t\t\t(thermal_bridge_width 0.5)\n\t\t)\n\t\t(polygon\n\t\t\t(pts {xy})\n\t\t)\n\t)")


def footprint():
    half_w, half_l = WIDTH / 2, LENGTH / 2
    usb_top = -half_l - USB_OVERHANG
    pads = [pad(n, 1, i) for i, n in enumerate(RIGHT_PINS)]
    pads += [pad(n, -1, i) for i, n in enumerate(LEFT_PINS)]
    pad_reach = ROW_SPACING / 2 + LEG_OFFSET + PAD_SIZE[0] / 2
    sockets = [rect("F.SilkS", round(s * ROW_SPACING / 2 - SOCKET_HALF_WIDTH, 3), pin_y(0) - PITCH / 2,
                    round(s * ROW_SPACING / 2 + SOCKET_HALF_WIDTH, 3), pin_y(7) + PITCH / 2, 0.12) for s in (-1, 1)]
    marker = (f"\t(fp_circle\n\t\t(center {pad_reach + 0.6} {pin_y(0)})\n\t\t(end {pad_reach + 0.9} {pin_y(0)})\n"
              f'{stroke(0.3)}\n\t\t(fill yes)\n\t\t(layer "F.SilkS")\n\t\t(uuid "{u()}")\n\t)')
    parts = [
        '(footprint "ESP32-C3_SuperMini_Sockets"', "\t(version 20260206)", '\t(generator "heater-controller")',
        '\t(layer "F.Cu")',
        '\t(descr "ESP32-C3 super mini (18 x 22 mm, USB-C overhangs 1.5 mm) on two 1x8 SMD female sockets 2.54 mm; '
        'pins 1-8 right: 5V GND 3V3 GPIO4..0, pins 9-16 left: GPIO5..10 GPIO20 GPIO21, USB end first")',
        '\t(tags "ESP32-C3 super mini module socket SMD")',
        label("REF**", half_l + 1.5, "F.SilkS", "Reference"),
        label("ESP32-C3_SuperMini_Sockets", half_l + 3.0, "F.Fab", "Value"),
        "\t(attr smd)",
        rect("F.Fab", -half_w, -half_l, half_w, half_l, 0.1),
        rect("F.Fab", -USB_WIDTH / 2, usb_top, USB_WIDTH / 2, -half_l, 0.1),
        rect("F.CrtYd", -pad_reach - 0.25, usb_top - 0.25, pad_reach + 0.25, half_l + 0.25, 0.05),
        *sockets, marker, label("USB", -half_l + 1.5), label("ANTENNA", half_l - 1.0),
        *pads, antenna_keepout(), "\t(embedded_fonts no)", socket_model(1), socket_model(-1), ")",
    ]
    return "\n".join(parts) + "\n"


if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else "heater-controller.pretty/ESP32-C3_SuperMini_Sockets.kicad_mod"
    with open(target, "w") as out:
        out.write(footprint())
