# viessmann-optolink-esphome

[Français](README.md) · **English**

DIY adapter that controls a Viessmann **Vitodens 222-W** gas boiler (wall-hung, built-in hot water tank; Vitotronic 200 controller type HO1B, Optolink Device ID `20CB`) from Home Assistant through its **Optolink** optical interface, reading and writing its *datapoints* (boiler temperature, room setpoint, operating mode, economy mode, fault).

ESPHome firmware on an ESP32-C3 super mini; `P300` protocol; `optolink` component from ESPHome PR [#4453](https://github.com/esphome/esphome/pull/4453).

> [!NOTE]
> **Project status.** The circuit (IR adapter on a breadboard) and the firmware **work on the boiler**: reading temperatures and writing the setpoint and mode are validated, on a Wemos D1 mini. The project is moving to an ESP32-C3 super mini (smaller, UART dedicated to the Optolink, logs over USB): schematic and firmware are ported, the port is **still to be validated on the boiler**. The **PCB** (`hardware/`) is **final** around the C3 (U-shaped board lying flat, everything through-hole and removable, off-board optical head): DRC with no error or warning, order files to solder it yourself or have JLCPCB assemble it. The **enclosure** (`enclosure/`) is final and sized for it.

> [!TIP]
> **Ready-made boards.** I may have assembled boards in stock (JLCPCB makes 5 at least): if you want one, get in touch by opening an issue on this repository.

**Keywords**: Viessmann Vitodens 222-W, Vitotronic 200 HO1B, gas boiler, Optolink, optical interface, IR adapter, Device ID `20CB`, P300 / VS2 protocol, OpenV, vcontrold, ESPHome, Home Assistant, home automation, ESP32-C3, ESP32-C3 super mini, HLK-PM01, KiCad PCB, JLCPCB, 3D-printed enclosure, Tado thermostat replacement.

## Repository layout

| Folder | Content |
|---|---|
| `firmware/` | ESPHome configuration: `common.yaml` (Wi-Fi, API, OTA, LED, diagnostics), `controlleur-chaudiere.yaml` (Optolink), `test-connectivity.yaml` (fake entities), `secrets.example.yaml` |
| `hardware/` | dedicated board, KiCad 10 project: schematic (`heater-controller.kicad_sch`), PCB (`.kicad_pcb`), C3 super mini symbol (`.kicad_sym`), isolation rules (`.kicad_dru`), project footprints (`heater-controller.pretty/`); `scripts/`: `export.sh` (manufacturing files and exports), `footprints.py` (writes the footprints), `jlcpcb-files.py` (LCSC cart, JLCPCB BOM and CPL), `placements.py` (part centres for the CPL); `exports/` (written by `export.sh`): schematic, 1:1 board, side and 3D renders, `.step` and `.stl` models for the enclosure (Fusion 360); `fabrication/`: order files, not versioned |
| `enclosure/` | 3D-printed enclosure clipped onto the Optolink port, sized for the U-shaped board: two interlocking half shells (`heater-enclosure-left-shell.stl`, `-right-shell.stl`), the sliding lid (`-lid.stl`) and the plug that clips onto the Optolink (`-optical-plug.stl`); the four parts laid out on the print bed (`print-setup.stl`); Fusion 360 source `heater-enclosure.f3d` |
| `knowledge/` | design notes, in French: `architecture.md` (roles, contract with the controller, safety), `datapoints-optolink.md`, `pression-circuit-chauffage.md`, Viessmann manuals (`manuals/`), optolink component doc, photos |

## Hardware

| Part | Role |
|---|---|
| ESP32-C3 super mini | Wi-Fi + UART to the Optolink (GPIO4/GPIO3), logs over native USB |
| IR LED (e.g. SIR 204 EVL) + 220 Ω | transmits to the boiler |
| Phototransistor (e.g. SFH 309 FA) + 10 kΩ | receives |

Wiring (see `knowledge/viessmann-optolink-esphome.pdf`, p. 2):

| C3 super mini | Connected to |
|---|---|
| `3V3` | 220 Ω resistor → IR LED anode; 10 kΩ resistor → phototransistor collector |
| `GPIO4` (TX) | IR LED cathode |
| `GPIO3` (RX) | phototransistor collector |
| `GND` | phototransistor emitter |

The IR LED faces the boiler's phototransistor and vice versa (Optolink "V" mark).

## Dedicated board (`hardware/`)

![Schematic](hardware/exports/heater-controller-schematic.svg)

Open `hardware/heater-controller.kicad_pro` in KiCad 10, or online with [KiCanvas](https://kicanvas.org/?github=https://github.com/Plokkke/viessmann-optolink-esphome/blob/main/hardware/heater-controller.kicad_sch). The board (74 × 35.5 mm, 2 layers) sits **parallel to the floor**, so perpendicular to the boiler front, and rests, unfixed, on four side ledges of the enclosure. It is an **inverted U**: the HLK lying on the bar, 230 V on the left leg, the C3 on the right leg. The notch between the legs (22 mm wide, 12.5 mm deep) separates 230 V from low voltage and lets the 230 V cable reach the terminal block.

The 230 V comes in through the optical plug: the L and N wires go up through the 6 × 6 mm slot in the bottom of the plug, through the hole in the enclosure front, under the board (4 mm of free height) and back up through the notch to the terminal block. Under the board they stay left of the half-shell joint teeth (only 2.8 mm in the middle of the floor) and away from the HLK 5 V pins (0.7 mm above the floor): the free lane is under the HLK, between its 230 V and 5 V pins, with no copper on the back. The optical head lead goes through the upper right part of the plug, away from the 230 V wires. **Everything is through-hole and removable**: C3 on sockets, optical head on a connector, 230 V on a screw terminal, fuse in a holder.

| Ref. | Part | Footprint | Location |
|---|---|---|---|
| PS1 | HLK-PM01 (230 V → 5 V, 3 W) | `Converter_ACDC_HLK-PM01`, from the Hi-Link datasheet (34 × 20 × 15 mm) | U bar, lying: 230 V pins on the left, 5 V pins on the right towards the C3 |
| F1 | T1A fuse (value recommended by Hi-Link) | TR5 fuse holder, 5.08 mm pitch, 1.0 mm holes | left leg, bottom left |
| RV1 | Bourns MOV-07D431K varistor (275 VAC) | `RV_Disc_D9mm_W4.8mm_P5mm_Inline`: inline leads at 5 mm pitch, 1.0 mm holes, 9 × 4.8 mm disc | left of the HLK, above the fuse |
| J1 | 2-way screw terminal, L and N wires from plug **96** (separate 0.75 mm² flexible wires with ferrules) | `TerminalBlock_Kefa_KF128-5.08_1x02`: Kefa KF128, 5.08 mm pitch, 1.4 mm holes, 10.16 × 10.7 × 14.1 mm | left leg, bottom, right of the fuse, opening towards the notch; terminal 1 = L, terminal 2 = N |
| J2 | optical head connector: `GND` `RX` `TX` `LED+` | 4-pin vertical JST PH (B4B-PH-K-S), 2 mm pitch, holes widened to 0.9 mm | top right, above the C3; 4-wire JST PH lead to D1 and Q1 soldered at the far end |
| J3, J4 | C3 female sockets (pins 1–8 and 9–16) | KiCad's `PinSocket_1x08_P2.54mm_Vertical`: 1×8 through-hole female socket, 8.5 mm high | right leg, 15.24 mm apart; C3 antenna against the right edge, USB towards the HLK |
| R1 | 220 Ω, IR LED current | axial, 7.62 mm pitch | top right, next to J2 |
| R2 | 10 kΩ, phototransistor pull-up | axial, 7.62 mm pitch | top right, next to J2 |

D1 (IR LED) and Q1 (phototransistor) are **off board**: pressed into the 3 mm holes of the plug (axes 14.0 mm apart), wired to J2 by the lead. The C3 (MOD1) is not soldered: in the schematic it connects through J3 and J4; on the board, a pad-less outline shows where it sits and keeps copper away from the antenna.

The project footprints are written by `hardware/scripts/footprints.py`, from the parts' datasheets. The C3 row spacing, 15.24 mm (0.6″, breadboard-compatible module), comes from [ProtoSupplies](https://protosupplies.com/product/esp32c3-supermini/). Pins 1–8 `5V GND 3V3 GPIO4…0` are on one side and pins 9–16 `GPIO5…10 GPIO20 GPIO21` on the other; the first pin is 1.27 mm from the USB edge.

Routing:

- **230 V**: 1 mm tracks, all on the front. The varistor comes first: the line goes from the fuse to the varistor, then from the varistor to the HLK.
- **5 V, GND and signals**: 0.3 mm tracks on the front, from the HLK and J2 to socket J3, except RX, which runs on the back from J2 to J3 (it crosses TX). 3V3 runs between pins 6 and 7 of J3. J4 carries no signal: it only holds the C3.
- **No ground plane** (**DÉCIDÉ**): with a 4800-baud UART and a C3 that has its own ground plane, plain tracks are enough, and no copper can end up under the antenna.

DRC rules require ≥ 6 mm between 230 V and low voltage and ≥ 2.5 mm between 230 V conductors. Only the two J1 terminals are exempt: their gap is the block's rated pitch.

| Front | Back | 3D view |
|---|---|---|
| ![Top](hardware/exports/heater-controller-top.png) | ![Bottom](hardware/exports/heater-controller-bottom.png) | ![3D](hardware/exports/heater-controller-3d.png) |

DRC (`kicad-cli pcb drc --schematic-parity`) finds no error, no warning, no missing connection and no schematic mismatch.

### Ordering

Every part is through-hole: the same board can be built in two ways. `hardware/scripts/export.sh` reruns DRC (it stops if it finds an error), then writes to `hardware/fabrication/` (not versioned):

- `heater-controller-gerbers.zip`, the board, to upload as is to JLCPCB in both cases;
- `hand-soldered/heater-controller-lcsc-cart.csv`, **hand soldering**: the LCSC cart of every part for 5 boards, fuse holder and fuse included, to upload to the LCSC *BOM Tool*. Both orders can ship together: send the JLCPCB order to the LCSC warehouse, then add it at the LCSC checkout;
- `jlcpcb-assembly/heater-controller-bom.csv` and `-cpl.csv`, **JLCPCB assembly**, no LCSC order: the list and positions of every part (through-hole assembly). JLCPCB solders the fuse holder but ships no loose parts: the TR5 T1A 250 V time-lag fuse is bought separately and clipped in by hand. The CPL follows JLCPCB's KiCad guide (`Designator,Mid X,Mid Y,Rotation,Layer`, in mm) and gives the **centre** of each part, the middle of its pads, computed by `placements.py`: KiCad exports the footprint origin, which is pin 1 on through-hole parts (15 mm off for the HLK). Check the part orientations in the JLCPCB preview, which has its own reference orientation for each part.

Every part carries its LCSC number in the schematic (`LCSC` field); `jlcpcb-files.py` derives both sets of files from it. `placements.py` runs with KiCad's Python (`pcbnew` module); `export.sh` looks for it in the KiCad app on macOS, or in `$KICAD_PYTHON`. The script also regenerates the renders, the STEP, the STL and the SVGs.

Board settings (JLCPCB): 2 layers, 1.6 mm FR-4, 1 oz copper, lead-free HASL, 5 boards (the manufacturing minimum), and 5 assembled boards if JLCPCB assembles. The milling bit rounds the inner corners of the U (about 0.5 mm radius), which does not matter.

Cost (JLCPCB quote, November 2026), for 5 boards: about $60 for JLCPCB manufacturing and assembly, plus about €15 of fuses and JST leads, sold in packs; printing the enclosure is negligible (about €1 at a fablab). That is **€14 to €17 per board**, but **about €70 for a single board** without loose parts at hand: boards, assembly and packs are paid as a whole.

Why everything is through-hole: the HLK and the terminal block do not exist as SMD parts, so JLCPCB solders through-hole parts anyway (a manual soldering fee per order, then about $0.016 per joint). Moving the rest to SMD would add the SMD line (setup, stencil, fee per non-basic part) without removing anything. To solder the sockets yourself, plug both onto the C3 before soldering, so the module holds them at its own spacing.

Parts (LCSC stock and prices checked on 2026-10-27); the footprints follow their datasheets, another part number may not fit:

| Ref. | Item | Supplier | Price |
|---|---|---|---|
| PS1 | Hi-Link HLK-PM01, through-hole pins | LCSC C209903 | $2.74 |
| F1 | Littelfuse 56000001009 TR5 fuse holder | LCSC C142909 | $0.76 |
| F1 | Littelfuse 37211000001 TR5 T1A 250 V time-lag fuse (long leads, cut to ~4 mm) | LCSC C142808 | $0.22 (by 5) |
| RV1 | Bourns MOV-07D431K varistor | LCSC C1528105 | $0.14 (by 5) |
| J1 | Kefa KF128-5.08-2P-AA screw terminal (250 V, 24 A, up to 2.5 mm²) | LCSC C474952 | $0.19 (by 5) |
| J2 | JST B4B-PH-K-S header | LCSC C131334 | $0.05 (by 10) |
| — | 200 mm 4-wire JST PH lead, tinned ends (Adafruit 4045) | DigiKey 1528-2825-ND | €0.84 |
| J3, J4 | BOOMELE 1×8 through-hole female sockets, 8.5 mm high; male pins to solder on the C3 | LCSC C27438 | — |
| R1, R2 | 220 Ω and 10 kΩ, metal film, 1/4 W, UNI-ROYAL MFR0W4F2200A50 and MFR0W4F1002A50 | LCSC C57439, C57436 | — |
| D1, Q1 | 3 mm IR LED (SIR 204 EVL) and 3 mm phototransistor (SFH 309 FA), from the prototype | own stock | — |

To check before ordering:

- **the C3 row spacing**: if the module, with its pins soldered, plugs into a breadboard across the centre channel, 15.24 mm is right;
- **the HLK-PM01**: the footprint follows the Hi-Link datasheet (5 V pins 15.4 mm apart, 29.4 mm from the 230 V pins), with 1.2 mm holes to absorb the ±8 % tolerance. A different module, or one with pads, will not fit;
- **a 1:1 print** of `hardware/exports/heater-controller-pcb.svg`: lay the C3, the HLK and the terminal block on it;
- **the enclosure**: the assembled board is 74 × 35.5 × 20.1 mm: 3.3 mm of HLK pins underneath, the HLK (15 mm) and the plugged C3 (8.5 mm socket, 2.5 mm header spacer, C3 and USB-C: about 15.2 mm) on top. There is no Kefa model for the terminal block: `heater-controller.stl` uses the Phoenix MKDS 1,5 it copies (13.8 mm instead of 14.1). The board goes in through the lid opening, between rims 75.8 mm apart (0.9 mm of play per side), and slides onto four 4 mm high ledges that stick out 5 mm from the walls: 1.7 mm of support under each edge, no part under the board closer than 2.7 mm to an edge. With the lid closed it has 80.6 × 39.2 × 27 mm: 3.3 mm of play per side across the width, 3.7 mm in depth, 0.7 mm under the HLK pins and 5 mm above the HLK and the C3.

Once on the boiler, the C3 is powered with 5 V by the HLK-PM01, **never at the same time as USB**: on most C3 super mini boards the `5V` pin is tied straight to the USB-C VBUS, so the external 5 V would flow back into the computer's USB port. To check that the LED emits, look at it through a phone camera.

## Firmware

```sh
uv tool install esphome
cp firmware/secrets.example.yaml firmware/secrets.yaml   # then fill in the values
cd firmware
esphome run test-connectivity.yaml --device /dev/cu.usbmodemXXXX   # optional: fake entities, no boiler needed
esphome run controlleur-chaudiere.yaml --device /dev/cu.usbmodemXXXX   # first flash, C3 off the board (the HLK hides its USB-C; hold BOOT while plugging if no port shows up)
esphome run controlleur-chaudiere.yaml --device controlleur-chaudiere.local   # then over the air
esphome logs controlleur-chaudiere.yaml --device controlleur-chaudiere.local   # logs over Wi-Fi, or over USB when off mains
```

To trace exchanges with the boiler: `optolink.logger: true` and `logger.level: DEBUG`.

## Datapoints

Addresses depend on the Vitotronic model: device and datapoint lists on the [OpenV wiki](https://github.com/openv/openv/wiki) (in German). One value is read every 10 s by default: set `update_interval` per entity, the optical interface is slow.

| Entity | Address | Type |
|---|---|---|
| Boiler Temperature | `0xA309` | sensor, 2 bytes, ÷ 100 |
| Disturbance | `0x0A82` | binary sensor |
| Room Temperature Setpoint | `0x2306` | number, 3–37 °C |
| Economy mode | `0x2302` | switch |
| Operation mode | `0x2323` | select (off / hot water only / heating + hot water) |

## Caveats

- **Unofficial component**: PR #4453 was closed without being merged. It builds with ESPHome 2026.10, but a future ESPHome release may break it; if so, pin the last working ESPHome version.
- **No other room controller**: a Tado thermostat overwrote the setpoint a few seconds after each write. It has been disconnected; the setpoint is now driven by this controller only.
- **Boiler restart**: the component suspends communication for 20 s (`communication_suspension`) when the boiler stops answering, otherwise its startup hangs.
- **Antenna**: the C3 super mini ceramic antenna is poor on many batches; `wifi.output_power: 8.5dB` keeps the link stable. Check `Wi-Fi signal` in the boiler room.
