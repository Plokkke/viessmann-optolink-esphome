# viessmann-optolink-esphome

**Français** · [English](README.en.md)

Adaptateur DIY qui pilote la chaudière Viessmann **Vitodens 222-W** (murale, ballon intégré ; régulation Vitotronic 200 type HO1B, Device ID Optolink `20CB`) depuis Home Assistant par l'interface optique **Optolink**, en lisant et en écrivant ses *datapoints* (température de chaudière, consigne d'ambiance, mode de fonctionnement, mode économie, défaut).

Firmware ESPHome sur un ESP32-C3 super mini ; protocole `P300` ; composant `optolink` de la PR ESPHome [#4453](https://github.com/esphome/esphome/pull/4453).

> [!NOTE]
> **État du projet.** Le montage (adaptateur IR sur plaque d'essai) et le firmware **fonctionnent sur la chaudière** : lecture des températures et écriture de la consigne et du mode validées, sur un Wemos D1 mini. **DÉCIDÉ** : passage à l'ESP32-C3 super mini (plus compact, UART dédié à l'Optolink, logs par USB) ; le schéma et le firmware sont portés, le portage reste **à valider sur la chaudière**. Le **circuit imprimé** (`hardware/`) est **finalisé** autour du C3 (carte en U posée à plat, tout traversant et démontable, tête optique déportée) : DRC sans erreur ni avertissement, fichiers de commande pour le souder soi-même ou le faire monter par JLCPCB. Le **boîtier** (`enclosure/`) est finalisé à ses dimensions.

> [!TIP]
> **Cartes toutes faites.** J'ai peut-être en stock des cartes déjà montées (JLCPCB en fabrique 5 au minimum) : si ça vous intéresse, écrivez-moi en ouvrant une *issue* sur ce dépôt.

**Mots-clés** : Viessmann Vitodens 222-W, Vitotronic 200 HO1B, chaudière gaz, Optolink, interface optique, adaptateur IR, Device ID `20CB`, protocole P300 / VS2, OpenV, vcontrold, ESPHome, Home Assistant, domotique, ESP32-C3, ESP32-C3 super mini, HLK-PM01, circuit imprimé KiCad, JLCPCB, boîtier imprimé en 3D, remplacement du thermostat Tado.

## Arborescence

| Dossier | Contenu |
|---|---|
| `firmware/` | configuration ESPHome : `common.yaml` (Wi-Fi, API, OTA, LED, diagnostic), `controlleur-chaudiere.yaml` (Optolink), `test-connectivity.yaml` (entités factices), `secrets.example.yaml` |
| `hardware/` | carte dédiée, projet KiCad 10 : schéma (`heater-controller.kicad_sch`), circuit imprimé (`.kicad_pcb`), symbole du C3 super mini (`.kicad_sym`), règles d'isolement (`.kicad_dru`), empreintes du projet (`heater-controller.pretty/`) ; `scripts/` : `export.sh` (fabrication et exports), `footprints.py` (écrit les empreintes), `jlcpcb-files.py` (panier LCSC, BOM et CPL JLCPCB), `placements.py` (centres des pièces pour le CPL) ; `exports/` (générés par `export.sh`) : rendus du schéma, de la carte à l'échelle 1, des faces et en 3D, modèles `.step` et `.stl` pour le boîtier (Fusion 360) ; `fabrication/` : fichiers de commande, non versionnés |
| `enclosure/` | boîtier imprimé en 3D, fixé sur le port Optolink, dimensionné pour la carte en U : deux demi-coques (`heater-enclosure-left-shell.stl`, `-right-shell.stl`) qui s'emboîtent, le couvercle coulissant (`-lid.stl`) et la fiche qui se clipse sur l'Optolink (`-optical-plug.stl`) ; les quatre pièces posées sur le plateau d'impression (`print-setup.stl`) ; source Fusion 360 `heater-enclosure.f3d` |
| `knowledge/` | `architecture.md` (rôles, contrat avec la régulation, sécurité), `datapoints-optolink.md`, `pression-circuit-chauffage.md`, notices Viessmann (`manuals/`), doc du composant optolink, photos |

## Matériel

| Composant | Rôle |
|---|---|
| ESP32-C3 super mini | Wi-Fi + UART vers l'Optolink (GPIO4/GPIO3), logs par l'USB natif |
| LED IR (ex. SIR 204 EVL) + 220 Ω | émission vers la chaudière |
| Phototransistor (ex. SFH 309 FA) + 10 kΩ | réception |

Câblage (cf. `knowledge/viessmann-optolink-esphome.pdf`, p. 2) :

| C3 super mini | Branché sur |
|---|---|
| `3V3` | résistance 220 Ω → anode de la LED IR ; résistance 10 kΩ → collecteur du phototransistor |
| `GPIO4` (TX) | cathode de la LED IR |
| `GPIO3` (RX) | collecteur du phototransistor |
| `GND` | émetteur du phototransistor |

La LED IR est alignée sur le phototransistor de la chaudière et inversement (repère « V » de l'Optolink). Un repère au scotch indique, sur l'adaptateur, le côté `TX` (LED IR) et le côté `RX` (phototransistor), pour le monter dans le bon sens.

## Carte dédiée (`hardware/`)

![Schéma](hardware/exports/heater-controller-schematic.svg)

Ouvrir `hardware/heater-controller.kicad_pro` dans KiCad 10, ou en ligne sur [KiCanvas](https://kicanvas.org/?github=https://github.com/Plokkke/viessmann-optolink-esphome/blob/main/hardware/heater-controller.kicad_sch). La carte (74 × 35,5 mm, 2 couches) se place **parallèle au sol**, donc perpendiculaire à la façade de la chaudière, et repose sans fixation sur quatre cales latérales du boîtier. Elle a la forme d'un **U renversé** : le HLK couché sur la barre, le 230 V sur la jambe gauche, le C3 sur la jambe droite. L'encoche entre les jambes (22 mm de large, 12,5 mm de profondeur) sépare le 230 V de la basse tension et laisse passer le câble 230 V jusqu'au bornier.

Le 230 V entre par la fiche optique : les fils L et N montent par la fente de 6 × 6 mm du fond de la fiche, traversent le trou de la façade du boîtier, passent sous la carte (4 mm de hauteur libre) et remontent par l'encoche jusqu'au bornier. Sous la carte, ils restent à gauche des dents d'assemblage des demi-coques (2,8 mm seulement au milieu du fond) et loin des broches 5 V du HLK (0,7 mm au-dessus du fond) : la voie libre est sous le HLK, entre ses broches 230 V et 5 V, sans cuivre en face arrière. La nappe de la tête optique passe par la partie haute droite de la fiche, à l'écart des fils 230 V. **Tout est traversant et démontable** : C3 sur barrettes, tête optique sur une fiche, 230 V sur bornier, fusible sur porte-fusible.

| Réf. | Composant | Empreinte | Place |
|---|---|---|---|
| PS1 | HLK-PM01 (230 V → 5 V, 3 W) | `Converter_ACDC_HLK-PM01`, d'après la fiche Hi-Link (34 × 20 × 15 mm) | barre du U, couché : broches 230 V à gauche, broches 5 V à droite vers le C3 |
| F1 | fusible T1A (valeur conseillée par Hi-Link) | porte-fusible TR5, pas de 5,08 mm, trous de 1,0 mm | jambe gauche, en bas à gauche |
| RV1 | varistance Bourns MOV-07D431K (275 V AC) | `RV_Disc_D9mm_W4.8mm_P5mm_Inline` : pattes alignées au pas de 5 mm, trous de 1,0 mm, disque de 9 × 4,8 mm | à gauche du HLK, au-dessus du fusible |
| J1 | bornier à vis 2 points, fils L et N de la fiche **96** (fils souples séparés de 0,75 mm² avec embout) | `TerminalBlock_Kefa_KF128-5.08_1x02` : Kefa KF128, pas de 5,08 mm, trous de 1,4 mm, 10,16 × 10,7 × 14,1 mm | jambe gauche, en bas, à droite du fusible, ouvert vers l'encoche ; borne 1 = L, borne 2 = N |
| J2 | fiche de la tête optique : `GND` `RX` `TX` `LED+` | JST PH 4 broches vertical (B4B-PH-K-S), pas de 2 mm, trous agrandis à 0,9 mm | en haut à droite, au-dessus du C3 ; nappe JST PH 4 fils vers D1 et Q1 soudées au bout |
| J3, J4 | barrettes femelles du C3 (broches 1–8 et 9–16) | `PinSocket_1x08_P2.54mm_Vertical` de KiCad : barrette femelle traversante 1×8, 8,5 mm de haut | jambe droite, à 15,24 mm d'entraxe ; C3 antenne contre le bord droit, USB vers le HLK |
| R1 | 220 Ω, courant de la LED IR | axiale, pas de 7,62 mm | en haut à droite, à côté de J2 |
| R2 | 10 kΩ, tirage du phototransistor | axiale, pas de 7,62 mm | en haut à droite, à côté de J2 |

D1 (LED IR) et Q1 (phototransistor) sont **hors carte** : enfoncés dans les trous de 3 mm de la fiche (axes à 14,0 mm), reliés à J2 par la nappe. Le C3 (MOD1) n'est pas soudé : sur le schéma, il est branché par J3 et J4 ; sur la carte, un contour sans pastilles montre sa place et interdit le cuivre sous l'antenne.

Les empreintes du projet sont produites par `hardware/scripts/footprints.py`, à partir des fiches techniques des pièces. L'entraxe des rangées du C3, 15,24 mm (0,6″, module compatible plaque d'essai), vient de [ProtoSupplies](https://protosupplies.com/product/esp32c3-supermini/). Les broches 1–8 `5V GND 3V3 GPIO4…0` sont d'un côté, les broches 9–16 `GPIO5…10 GPIO20 GPIO21` de l'autre ; la première broche est à 1,27 mm du bord USB.

Routage :

- **230 V** : pistes de 1 mm, toutes sur la face avant. La varistance est placée en tête : la phase va du fusible à la varistance, puis de la varistance au HLK.
- **5 V, GND et signaux** : pistes de 0,3 mm en face avant, du HLK et de J2 jusqu'à la barrette J3, sauf RX qui passe en face arrière de J2 à J3 (il croise TX). La 3V3 passe entre les broches 6 et 7 de J3. J4 ne porte aucun signal : elle tient seulement le C3.
- **Pas de plan de masse** (**DÉCIDÉ**) : avec un UART à 4800 bauds et un C3 qui a son propre plan de masse, des pistes simples suffisent, et aucun cuivre ne risque de passer sous l'antenne.

Les règles DRC imposent ≥ 6 mm entre le 230 V et la basse tension et ≥ 2,5 mm entre conducteurs 230 V. Seules les deux bornes de J1 y échappent : leur écart est celui, normalisé, du bornier.

| Face avant | Face arrière | Vue 3D |
|---|---|---|
| ![Dessus](hardware/exports/heater-controller-top.png) | ![Dessous](hardware/exports/heater-controller-bottom.png) | ![3D](hardware/exports/heater-controller-3d.png) |

Le DRC (`kicad-cli pcb drc --schematic-parity`) ne trouve ni erreur, ni avertissement, ni liaison manquante, ni écart avec le schéma.

### Commander

Toutes les pièces sont traversantes : la même carte se monte de deux façons. `hardware/scripts/export.sh` relance le DRC (il s'arrête s'il trouve une erreur) puis produit, dans `hardware/fabrication/` (non versionné) :

- `heater-controller-gerbers.zip`, le circuit, à déposer tel quel chez JLCPCB dans les deux cas ;
- `hand-soldered/heater-controller-lcsc-cart.csv`, **soudure à la main** : le panier LCSC de toutes les pièces pour 5 cartes, porte-fusible et fusible compris, à déposer dans le *BOM Tool* de LCSC. Les deux commandes peuvent partir ensemble : expédier la commande JLCPCB vers l'entrepôt LCSC, puis l'ajouter au paiement LCSC ;
- `jlcpcb-assembly/heater-controller-bom.csv` et `-cpl.csv`, **montage par JLCPCB**, sans commande LCSC : la liste et les positions de toutes les pièces (assemblage traversant). JLCPCB soude le porte-fusible mais n'envoie pas de pièces en vrac : le fusible TR5 T1A 250 V temporisé s'achète à part et se clipse à la main. Le CPL suit le format de la notice KiCad de JLCPCB (`Designator,Mid X,Mid Y,Rotation,Layer`, en mm) et donne le **centre** de chaque pièce, celui des pastilles, calculé par `placements.py` : KiCad exporte l'origine de l'empreinte, qui est la broche 1 des pièces traversantes (15 mm à côté pour le HLK). Vérifier l'orientation des pièces dans l'aperçu de JLCPCB, qui a sa propre orientation de référence par pièce.

Chaque pièce porte sa référence LCSC dans le schéma (champ `LCSC`) ; `jlcpcb-files.py` en tire les deux jeux de fichiers. `placements.py` tourne avec le Python de KiCad (module `pcbnew`) ; `export.sh` le cherche dans l'application KiCad sur macOS, ou dans `$KICAD_PYTHON`. Le script régénère aussi les rendus, le STEP, le STL et les SVG.

Réglages du circuit (JLCPCB) : 2 couches, FR-4 de 1,6 mm, cuivre de 1 oz, HASL sans plomb, 5 exemplaires (le minimum de fabrication), et 5 cartes montées si JLCPCB assemble. Les coins intérieurs du U seront arrondis par la fraise (rayon d'environ 0,5 mm), sans conséquence.

Prix de revient (devis JLCPCB, novembre 2026), pour 5 cartes : environ 60 $ de fabrication et de montage par JLCPCB, plus environ 15 € de fusibles et de câbles JST, vendus par lots ; l'impression du boîtier est négligeable (environ 1 € en fablab). Soit **14 à 17 € par carte**, mais **environ 70 € pour une seule carte** si on n'a pas les pièces au détail : les circuits, le montage et les lots se paient d'un bloc.

Pourquoi tout en traversant : le HLK et le bornier n'existent pas en CMS, donc JLCPCB soude du traversant de toute façon (forfait de soudure manuelle par commande, puis environ 0,016 $ par point). Passer le reste en CMS ajouterait la chaîne CMS (mise en route, pochoir, frais par référence hors catalogue de base) sans rien retirer. Pour souder les barrettes soi-même, les enficher sur le C3 avant de les souder : le module les tient alors à son entraxe.

Pièces (stock et prix LCSC relevés le 27/10/2026) ; les empreintes suivent leurs fiches techniques, une autre référence peut ne pas s'y monter :

| Réf. | Pièce | Fournisseur | Prix |
|---|---|---|---|
| PS1 | Hi-Link HLK-PM01, à broches traversantes | LCSC C209903 | 2,74 $ |
| F1 | porte-fusible TR5 Littelfuse 56000001009 | LCSC C142909 | 0,76 $ |
| F1 | fusible TR5 T1A 250 V temporisé Littelfuse 37211000001 (pattes longues, à couper à ~4 mm) | LCSC C142808 | 0,22 $ (par 5) |
| RV1 | varistance Bourns MOV-07D431K | LCSC C1528105 | 0,14 $ (par 5) |
| J1 | bornier à vis Kefa KF128-5.08-2P-AA (250 V, 24 A, jusqu'à 2,5 mm²) | LCSC C474952 | 0,19 $ (par 5) |
| J2 | embase JST B4B-PH-K-S | LCSC C131334 | 0,05 $ (par 10) |
| — | nappe JST PH 4 fils de 200 mm, bouts étamés (Adafruit 4045) | DigiKey 1528-2825-ND | 0,84 € |
| J3, J4 | barrettes femelles traversantes 1×8 BOOMELE, 8,5 mm de haut ; broches mâles à souder sur le C3 | LCSC C27438 | — |
| R1, R2 | 220 Ω et 10 kΩ, couche métallique, 1/4 W, UNI-ROYAL MFR0W4F2200A50 et MFR0W4F1002A50 | LCSC C57439, C57436 | — |
| D1, Q1 | LED IR 3 mm (SIR 204 EVL) et phototransistor 3 mm (SFH 309 FA), ceux du prototype | stock personnel | — |

À vérifier avant de commander :

- **l'entraxe du C3** : si le module, broches soudées, s'enfonce dans une plaque d'essai à cheval sur la gorge centrale, l'entraxe de 15,24 mm est le bon ;
- **le HLK-PM01** : l'empreinte suit la fiche Hi-Link (broches 5 V à 15,4 mm l'une de l'autre, à 29,4 mm des broches 230 V), avec des trous de 1,2 mm pour absorber la tolérance de ±8 %. Un module différent, ou à pastilles, ne s'y monte pas ;
- **l'impression à l'échelle 1** de `hardware/exports/heater-controller-pcb.svg` : y poser le C3, le HLK et le bornier ;
- **le boîtier** : la carte montée fait 74 × 35,5 × 20,1 mm : 3,3 mm de pattes du HLK en dessous, le HLK (15 mm) et le C3 enfiché (barrette de 8,5 mm, entretoise de 2,5 mm, C3 et USB-C : environ 15,2 mm) au-dessus. Le bornier n'a pas de modèle Kefa : `heater-controller.stl` reprend celui du Phoenix MKDS 1,5, dont il est la copie (13,8 mm au lieu de 14,1). La carte entre par l'ouverture du couvercle, entre des rebords écartés de 75,8 mm (0,9 mm de jeu par côté), et glisse sur quatre cales de 4 mm de haut qui dépassent de 5 mm des parois : 1,7 mm d'appui sous chaque bord, aucune pièce sous la carte à moins de 2,7 mm d'un bord. Couvercle fermé, elle dispose de 80,6 × 39,2 × 27 mm : 3,3 mm de jeu par côté en largeur, 3,7 mm en profondeur, 0,7 mm sous les pattes du HLK et 5 mm au-dessus du HLK et du C3.

Une fois sur la chaudière, le C3 est alimenté en 5 V par le HLK-PM01 : **jamais d'USB branché en même temps**. Sur la plupart des C3 super mini, la broche `5V` est reliée directement au VBUS de l'USB-C : le 5 V externe remonterait dans le port USB de l'ordinateur. Pour vérifier que la LED émet, regarder à travers l'appareil photo d'un téléphone.

## Firmware

### Prérequis

```sh
uv tool install esphome
cp firmware/secrets.example.yaml firmware/secrets.yaml   # puis renseigner les valeurs
```

`secrets.yaml` n'est pas versionné. Si l'appareil est déjà adopté dans Home Assistant, reprendre la clé API et le mot de passe OTA existants : en changer oblige à le réadopter.

### Test de connectivité (sans chaudière)

`test-connectivity.yaml` porte le même nom d'appareil que le firmware réel, mais remplace l'Optolink par des entités factices (température qui oscille, consigne, interrupteur). La LED du module (GPIO8) est pilotable depuis Home Assistant et clignote en cas d'erreur (Wi-Fi ou API perdus).

```sh
cd firmware
esphome run test-connectivity.yaml --device /dev/cu.usbmodemXXXX
```

On repasse ensuite sur `controlleur-chaudiere.yaml` par OTA.

### Premier flash (USB)

Le C3 se flashe **hors de la carte** : sur la carte, le HLK masque son port USB-C. On le flashe une fois par USB, on l'enfiche sur J3/J4, puis les mises à jour passent par le Wi-Fi (OTA).

```sh
cd firmware
esphome run controlleur-chaudiere.yaml --device /dev/cu.usbmodemXXXX
```

`ls /dev/cu.*` liste les ports (USB natif du C3 : aucun pilote). Si le module n'apparaît pas, le brancher en maintenant le bouton `BOOT` (GPIO9).

### Mises à jour (OTA Wi-Fi)

```sh
esphome run controlleur-chaudiere.yaml --device controlleur-chaudiere.local
```

### Logs

Les logs sortent par l'USB natif (`logger.hardware_uart: USB_SERIAL_JTAG`), hors secteur, ou par le Wi-Fi :

```sh
esphome logs controlleur-chaudiere.yaml --device controlleur-chaudiere.local
```

Pour tracer les échanges avec la chaudière : `optolink.logger: true` et `logger.level: DEBUG`.

## Datapoints

Les adresses dépendent du modèle de Vitotronic : liste des appareils et des datapoints sur le [wiki OpenV](https://github.com/openv/openv/wiki) (en allemand). Une valeur lue toutes les 10 s par défaut : régler `update_interval` sur chaque entité, l'interface optique est lente.

| Entité | Adresse | Type |
|---|---|---|
| Boiler Temperature | `0xA309` | capteur, 2 octets, ÷ 100 |
| Disturbance | `0x0A82` | capteur binaire |
| Room Temperature Setpoint | `0x2306` | nombre, 3–37 °C |
| Economy mode | `0x2302` | interrupteur |
| Operation mode | `0x2323` | sélection (arrêt / ECS seule / chauffage + ECS) |

## Points d'attention

- **Composant non officiel** : la PR #4453 a été fermée sans fusion. Elle compile avec ESPHome 2026.10, mais une version future d'ESPHome peut la casser ; dans ce cas, épingler la dernière version d'ESPHome qui fonctionne.
- **Pas d'autre commande d'ambiance** : le thermostat Tado réimposait sa propre consigne quelques secondes après chaque écriture. **DÉCIDÉ** : le Tado est débranché, la consigne est pilotée uniquement par ce contrôleur (vérifié le 2026-10-24 : la consigne de 25 °C n'a plus été écrasée).
- **Redémarrage de la chaudière** : le composant suspend la communication 20 s (`communication_suspension`) quand la chaudière ne répond plus, sinon son démarrage se bloque.
- **Antenne** : l'antenne céramique du C3 super mini est médiocre sur beaucoup de lots ; `wifi.output_power: 8.5dB` stabilise la liaison. Vérifier le signal (`Wi-Fi signal`) dans la chaufferie.
