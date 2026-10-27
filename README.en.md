# viessmann-optolink-esphome

[Français](README.md) · **English**

DIY adapter that controls a Viessmann **Vitodens 222-W** gas boiler (wall-hung, built-in hot water tank; Vitotronic 200 controller type HO1B, Optolink Device ID `20CB`) from Home Assistant through its **Optolink** optical interface, reading and writing its *datapoints* (boiler temperature, room setpoint, operating mode, economy mode, fault).

ESPHome firmware on an ESP32-C3 super mini; `P300` protocol; `optolink` component from ESPHome PR [#4453](https://github.com/esphome/esphome/pull/4453).

> [!NOTE]
> **Project status.** The circuit (IR adapter on a breadboard) and the firmware **work on the boiler**: reading temperatures and writing the setpoint and mode are validated, on a Wemos D1 mini. The project is moving to an ESP32-C3 super mini (smaller, UART dedicated to the Optolink, logs over USB): schematic and firmware are ported, the port is **still to be validated on the boiler**. The **PCB** (`hardware/`) is redrawn around the C3 (U-shaped board, everything removable, off-board optical head) and routed; it is **ready to order** once the checks listed below are done, and the **enclosure** is redrawn to fit it.

**Keywords**: Viessmann Vitodens 222-W, Vitotronic 200 HO1B, gas boiler, Optolink, optical interface, IR adapter, Device ID `20CB`, P300 / VS2 protocol, OpenV, vcontrold, ESPHome, Home Assistant, home automation, ESP32-C3, ESP32-C3 super mini, HLK-PM01, Tado thermostat replacement.

## Repository layout

| Folder | Content |
|---|---|
| `firmware/` | ESPHome configuration: `common.yaml` (Wi-Fi, API, OTA, LED, diagnostics), `controlleur-chaudiere.yaml` (Optolink), `test-connectivity.yaml` (fake entities), `secrets.example.yaml` |
| `hardware/` | dedicated KiCad board: schematic (`heater-controller.kicad_sch`, `.svg` render), PCB (`.kicad_pcb`, `-top.png` / `-bottom.png` / `-3d.png` renders), 3D model `heater-controller.step` for enclosure design, C3 super mini symbol (`heater-controller.kicad_sym`), project footprints (`heater-controller.pretty/`, written by `footprints.py`), isolation rules (`.kicad_dru`), manufacturing files (`export-fabrication.sh`) |
| `enclosure/` | 3D-printed enclosure clipped onto the Optolink port (`heater-enclosure.stl`), sized for the U-shaped board |
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

![Schematic](hardware/heater-controller.svg)

Open `hardware/heater-controller.kicad_pro` in KiCad 10, or online with [KiCanvas](https://kicanvas.org/?github=https://github.com/Plokkke/viessmann-optolink-esphome/blob/main/hardware/heater-controller.kicad_sch). The board (86 × 39.5 mm, 2 layers) sits **parallel to the boiler front**, in the wide part of the enclosure, and floats (no fixing). It is an **inverted U**: 230 V on the left leg, the optical head connector on the bar, the C3 on the right leg. The notch between the legs (24.5 mm) separates 230 V from low voltage and lets the 230 V cable reach the terminal block. **Everything is removable**: C3 on sockets, optical head on a connector, 230 V on a screw terminal, fuse in a holder.

| Ref. | Part | Footprint | Location |
|---|---|---|---|
| PS1 | HLK-PM01 (230 V → 5 V, 3 W) | `Converter_ACDC_HLK-PM01`, from the Hi-Link datasheet (34 × 20 × 15 mm) | left leg, upright: 230 V pins at the bottom, 5 V pins at the top towards the bar |
| F1 | T1A fuse (value recommended by Hi-Link) | TR5 fuse holder | left leg, top right |
| RV1 | 07D431K varistor (275 VAC) | 7 mm disc, 5 mm pitch | left leg, middle, between the fuse and the HLK |
| J1 | 2-way screw terminal, L and N wires from plug **96** (up to 1.5 mm² with ferrule) | Phoenix MKDS 1.5, 5.08 mm pitch | left leg, bottom, opening towards the notch |
| J2 | optical head connector: `GND` `RX` `TX` `LED+` | 4-pin vertical JST PH (B4B-PH-K-S), 2 mm pitch | U bar; 4-wire JST PH lead to D1 and Q1 soldered at the far end |
| J3, J4 | C3 female sockets (pins 1–8 and 9–16) | `PinSocket_1x08_P2.54mm_SMD_HX-ZQ`: hanxia 1×8 SMD socket (LCSC C48641756), staggered legs | right leg, 15.24 mm apart; C3 antenna against the top edge, USB down |
| R1 | 220 Ω, IR LED current | axial, 7.62 mm pitch | between the sockets, under the C3 |
| R2 | 10 kΩ, phototransistor pull-up | axial, 7.62 mm pitch | between the sockets, under the C3 |

D1 (IR LED) and Q1 (phototransistor) are **off board**: pressed into the 3 mm holes of the plug (axes 14.0 mm apart), wired to J2 by the lead. The C3 (MOD1) is not soldered: in the schematic it connects through J3 and J4; on the board, a pad-less outline shows where it sits and keeps copper away from the antenna.

The project footprints are written by `hardware/footprints.py`, from the parts' datasheets. The C3 row spacing, 15.24 mm (0.6″, breadboard-compatible module), comes from [ProtoSupplies](https://protosupplies.com/product/esp32c3-supermini/). Pins 1–8 `5V GND 3V3 GPIO4…0` are on one side and pins 9–16 `GPIO5…10 GPIO20 GPIO21` on the other; the first pin is 1.27 mm from the USB edge.

Routing:

- **230 V**: 1 mm tracks, all on the front. The varistor comes first: the line goes from the fuse to the varistor, then from the varistor to the HLK.
- **5 V and GND**: 0.7 mm tracks along the top edge, +5V on the back, GND on the front. GND runs under J2, then along the notch to the C3; that narrow passage stays at 0.3 mm.
- **Signals**: 0.3 mm tracks; RX runs above J2.
- **No ground plane** (**DÉCIDÉ**): with a 4800-baud UART and a C3 that has its own ground plane, 0.7 mm tracks are enough, and no copper can end up under the antenna.

DRC rules require ≥ 6 mm between 230 V and low voltage and ≥ 2.5 mm between 230 V conductors. Only the two J1 terminals are exempt: their gap is the block's rated pitch.

| Front | Back | 3D view |
|---|---|---|
| ![Top](hardware/heater-controller-top.png) | ![Bottom](hardware/heater-controller-bottom.png) | ![3D](hardware/heater-controller-3d.png) |

DRC (`kicad-cli pcb drc --schematic-parity`) finds no error, no missing connection and no schematic mismatch. Some silkscreen warnings remain: markings clipped by pads, which do not affect manufacturing.

### Ordering

`hardware/export-fabrication.sh` reruns DRC (it stops if it finds an error), then writes to `hardware/fabrication/` (not versioned):

- `heater-controller-gerbers.zip`, to upload as is to the manufacturer;
- `heater-controller-bom-jlcpcb.csv` and `heater-controller-cpl.csv`, the list and positions of the parts JLCPCB assembles: only J3 and J4, the parts that carry an LCSC number in the schematic;
- `heater-controller-bom.csv`, the full parts list.

The script also regenerates the renders, the STEP and the SVG.

Board settings (JLCPCB): 2 layers, 1.6 mm FR-4, 1 oz copper, lead-free HASL, 5 boards (the manufacturing minimum). The milling bit rounds the inner corners of the U (about 0.5 mm radius), which does not matter.

Having JLCPCB fit the sockets is **optional**: about $13 extra (setup, stencil, non-basic part fee), on 2 boards minimum. The row spacing does not depend on who solders: the pads set it. To solder them yourself, plug both sockets onto the C3 before soldering, so the module holds them at its own spacing.

To solder yourself:

| Ref. | Item |
|---|---|
| PS1 | genuine Hi-Link HLK-PM01, through-hole pins |
| F1 | TR5 fuse holder (Littelfuse 560) and TR5 T1A time-lag fuse (Littelfuse 372) |
| RV1 | 07D431K varistor |
| J1 | Phoenix MKDS 1,5/2-5,08 screw terminal (or any 5.08 mm pitch equivalent) |
| J2 | B4B-PH-K-S 4-pin vertical JST PH header, and a ready-made 4-wire JST PH lead |
| J3, J4 | 2 × hanxia HX PM2.54-1x8P TP H8.5-ZQ 1×8 SMD female sockets (LCSC C48641756), unless JLCPCB fits them; male pins to solder on the C3 |
| R1, R2 | 220 Ω and 10 kΩ, axial |
| D1, Q1 | 3 mm IR LED (SIR 204 EVL) and 3 mm phototransistor (SFH 309 FA) |

To check before ordering:

- **the C3 row spacing**: if the module, with its pins soldered, plugs into a breadboard across the centre channel, 15.24 mm is right;
- **the HLK-PM01**: the footprint follows the Hi-Link datasheet (5 V pins 15.4 mm apart, 29.4 mm from the 230 V pins), with 1.2 mm holes to absorb the ±8 % tolerance. A different module, or one with pads, will not fit;
- **a 1:1 print** of `hardware/heater-controller.svg`: lay the C3, the HLK and the terminal block on it;
- **the enclosure**: the board is 86 × 39.5 mm. The tallest part is the HLK (15 mm); the C3 on sockets stands about 13 mm high. The enclosure `enclosure/heater-enclosure.stl` gives 86.8 × 40.3 mm inside, about 0.4 mm of play per side, and 30.8 mm of depth.

Once on the boiler, the C3 is powered with 5 V by the HLK-PM01, **never at the same time as USB**: on most C3 super mini boards the `5V` pin is tied straight to the USB-C VBUS, so the external 5 V would flow back into the computer's USB port. To check that the LED emits, look at it through a phone camera.

## Firmware

```sh
uv tool install esphome
cp firmware/secrets.example.yaml firmware/secrets.yaml   # then fill in the values
cd firmware
esphome run test-connectivity.yaml --device /dev/cu.usbmodemXXXX   # optional: fake entities, no boiler needed
esphome run controlleur-chaudiere.yaml --device /dev/cu.usbmodemXXXX   # first flash, off mains (hold BOOT while plugging if no port shows up)
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
