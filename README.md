# viessmann-optolink-esphome

**Français** · [English](README.en.md)

Adaptateur DIY qui pilote la chaudière Viessmann **Vitodens 222-W** (murale, ballon intégré ; régulation Vitotronic 200 type HO1B, Device ID Optolink `20CB`) depuis Home Assistant par l'interface optique **Optolink**, en lisant et en écrivant ses *datapoints* (température de chaudière, consigne d'ambiance, mode de fonctionnement, mode économie, défaut).

Firmware ESPHome sur un Wemos D1 mini (ESP8266) ; protocole `P300` ; composant `optolink` de la PR ESPHome [#4453](https://github.com/esphome/esphome/pull/4453).

> [!NOTE]
> **État du projet.** Le montage (adaptateur IR sur plaque d'essai) et le firmware **fonctionnent sur la chaudière** : lecture des températures et écriture de la consigne et du mode validées. La **carte dédiée** (`hardware/`) et le **boîtier** associé ne sont **pas définitifs** : la carte n'a pas encore été fabriquée.

**Mots-clés** : Viessmann Vitodens 222-W, Vitotronic 200 HO1B, chaudière gaz, Optolink, interface optique, adaptateur IR, Device ID `20CB`, protocole P300 / VS2, OpenV, vcontrold, ESPHome, Home Assistant, domotique, ESP8266, Wemos D1 mini, HLK-PM01, remplacement du thermostat Tado.

## Arborescence

| Dossier | Contenu |
|---|---|
| `firmware/` | configuration ESPHome : `common.yaml` (Wi-Fi, API, OTA, LED, diagnostic), `controlleur-chaudiere.yaml` (Optolink), `test-connectivity.yaml` (entités factices), `secrets.example.yaml` |
| `hardware/` | carte dédiée KiCad : schéma (`heater-controller.kicad_sch`, rendu `.svg`), circuit imprimé (`.kicad_pcb`, rendus `-top.png` / `-bottom.png`), modèle 3D `heater-controller.step` pour le boîtier (Fusion 360), empreinte du D1 mini (`heater-controller.pretty/`), règles d'isolement (`.kicad_dru`) |
| `enclosure/` | boîtier imprimé en 3D, fixé sur le port Optolink (`.3mf` pour le slicer, `.stl`) |
| `knowledge/` | `architecture.md` (rôles, contrat avec la régulation, sécurité), `datapoints-optolink.md`, `pression-circuit-chauffage.md`, notices Viessmann (`manuals/`), doc du composant optolink, photos |

## Matériel

| Composant | Rôle |
|---|---|
| Wemos D1 mini (ESP8266) | Wi-Fi + UART0 vers l'Optolink |
| LED IR (ex. SIR 204 EVL) + 220 Ω | émission vers la chaudière |
| Phototransistor (ex. SFH 309 FA) + 10 kΩ | réception |

Câblage (cf. `knowledge/viessmann-optolink-esphome.pdf`, p. 2) :

| D1 mini | Branché sur |
|---|---|
| `3V3` | résistance 220 Ω → anode de la LED IR ; résistance 10 kΩ → collecteur du phototransistor |
| `TX` (GPIO1) | cathode de la LED IR |
| `RX` (GPIO3) | collecteur du phototransistor |
| `GND` | émetteur du phototransistor |

La LED IR est alignée sur le phototransistor de la chaudière et inversement (repère « V » de l'Optolink). Un repère au scotch indique, sur l'adaptateur, le côté `TX` (LED IR) et le côté `RX` (phototransistor), pour le monter dans le bon sens.

## Carte dédiée (`hardware/`)

![Schéma](hardware/heater-controller.svg)

Ouvrir `hardware/heater-controller.kicad_pro` dans KiCad 10, ou en ligne sur [KiCanvas](https://kicanvas.org/?github=https://github.com/Plokkke/viessmann-optolink-esphome/blob/main/hardware/heater-controller.kicad_sch). La carte (65 × 63 mm, 2 couches) reprend le montage ci-dessus et y ajoute l'alimentation 230 V → 5 V :

| Élément | Choix |
|---|---|
| Alimentation | HLK-PM01 sur la carte, fusible T500mA + varistance 10D561K, bornier J1 vers la fiche **96** de la Vitotronic (L en haut, N en bas) |
| D1 mini | sur le **dessus**, enfiché dans deux barrettes femelles 1×8 **CMS** (aucune patte ne traverse sous la zone optique) ; ordre physique, antenne vers le haut : `RST`…`3V3` à gauche, `TX`…`5V` à droite, `5V` en face de `3V3` |
| LED IR (D1) et phototransistor (Q1) | sur le **dessous**, axes optiques à **14,0 mm** (écartement des trous de la plaque actuelle), LED côté gauche vue de dessus |
| Résistances | CMS 0805, sous le D1 mini |
| Isolement | fente de 1,5 mm entre basse tension et 230 V ; règle DRC : ≥ 6 mm entre le 230 V et la basse tension, ≥ 2,5 mm entre conducteurs 230 V |

| Dessus | Dessous |
|---|---|
| ![Dessus](hardware/heater-controller-top.png) | ![Dessous](hardware/heater-controller-bottom.png) |

Le DRC (`kicad-cli pcb drc --schematic-parity`) passe sans erreur ; seul avertissement : la sérigraphie du HLK-PM01 enjambe la fente, ce qui est voulu.

À vérifier avant de commander :

- **le brochage de ton D1 mini** contre la sérigraphie (`RST`/`TX` en haut, `3V3`/`5V` en bas) ;
- **le support imprimé** : la carte remplace l'adaptateur sur plaque d'essai, la plaque (28,4 × 24 mm, détrompeur en « V ») se fixe sous la carte, centrée sur les deux composants optiques (contour sérigraphié au dos) ; le boîtier est à redessiner autour de la carte ;
- le porte-fusible 5×20 vertical est haut (≈ 20 mm) : un fusible TR5 (empreinte `Fuseholder_TR5_Littelfuse_No560_No460`) réduirait la hauteur.

Une fois sur la chaudière, la carte est alimentée en 5 V par les broches `5V` et `GND`, **jamais en même temps que l'USB**. Le D1 mini n'a pas toujours de diode de protection, et le 5 V externe peut remonter dans le port USB de l'ordinateur. Pour vérifier que la LED émet, regarder à travers l'appareil photo d'un téléphone.

## Firmware

### Prérequis

```sh
uv tool install esphome
cp firmware/secrets.example.yaml firmware/secrets.yaml   # puis renseigner les valeurs
```

`secrets.yaml` n'est pas versionné. Si l'appareil est déjà adopté dans Home Assistant, reprendre la clé API et le mot de passe OTA existants : en changer oblige à le réadopter.

### Test de connectivité (sans chaudière)

`test-connectivity.yaml` porte le même nom d'appareil que le firmware réel, mais remplace l'Optolink par des entités factices (température qui oscille, consigne, interrupteur). Les logs sortent aussi sur le port série, puisque l'UART0 est libre. La LED de la carte (GPIO2) est pilotable depuis Home Assistant et clignote en cas d'erreur (Wi-Fi ou API perdus).

```sh
cd firmware
esphome run test-connectivity.yaml --device /dev/cu.usbserial-XXXX
```

On repasse ensuite sur `controlleur-chaudiere.yaml` par OTA.

### Premier flash (USB)

Débrancher l'adaptateur IR avant de flasher : il occupe `TX`/`RX`, les mêmes broches que le port USB.

```sh
cd firmware
esphome run controlleur-chaudiere.yaml --device /dev/cu.usbserial-XXXX
```

`ls /dev/cu.*` liste les ports (puce CH340 du D1 mini : pilote inclus dans macOS).

### Mises à jour (OTA Wi-Fi)

```sh
esphome run controlleur-chaudiere.yaml --device controlleur-chaudiere.local
```

### Logs

L'UART0 est réservé à l'Optolink (`logger.baud_rate: 0`) : aucun log sur le port série. Les logs passent par le Wi-Fi :

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
- **Mémoire** : l'ESP8266 a peu de RAM ; éviter `web_server` et ajouter les datapoints avec parcimonie.
