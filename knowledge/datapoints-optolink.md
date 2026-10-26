# Datapoints Optolink — Vitotronic 200 HO1B (Device ID `20CB`, P300)

Ce qui est câblé dans le firmware est dans `firmware/controlleur-chaudiere.yaml` ; ce document liste tout ce qui est disponible.

## Identification

`DEVICE_INFO` : `Device ID: 20CB | Hardware Revision: 28 | Software Index: CB`. L'ID 20CB recouvre plusieurs listes Vitosoft, distinguées par l'index logiciel et l'octet `0x00F0` :

| Index logiciel | `0x00F0` | Variante Vitosoft |
|---|---|---|
| 0x28–0x45 | — | `VScotHO1_40` |
| 0x48–0x59 | — | `VScotHO1_72` |
| 0x5A–0x81 | — | `VScotHO1_90` |
| ≥ 0xC8 | 0x10 | `VScotHO1_200_10` |
| ≥ 0xC8 | 0x11–0x19 | `VScotHO1_200_11` (HO1B à partir de 04/2016) |

Index `CB` → famille `_200_1x` ; l'entité « Extended identification » (`0x00F0`) tranche. `_200_11` débloque la charge ECS unique (`0x65F5`) et, à tester, les compteurs de gaz.

## Confiance

- **A** : 20CB officiel (liste Viessmann Vitogate 200 pour 20CB HO1B, qui couvre B2LA = 222-W, et/ou base Vitosoft).
- **B** : 20CB communautaire, ou champ d'une structure.
- **C** : générique de la famille, à tester.

## Températures

| Nom | Adr. | Oct. | div | Signé | R/W | Conf. |
|---|---|---|---|---|---|---|
| Extérieure filtrée (30 min) | 0x5525 | 2 | 10 | oui | R | A |
| Extérieure amortie | 0x5527 | 2 | 10 | oui | R | A |
| Extérieure brute | 0x0800 | 2 | 10 | oui | R | B |
| Chaudière filtrée | 0x0810 | 2 | 10 | | R | A |
| Chaudière (variable LON) | 0xA309 | 2 | 100 | | R | B (vérifiée) |
| Consigne chaudière effective | 0x555A | 2 | 10 | | R | A |
| Consigne de départ A1M1 | 0x2544 | 2 | 10 | | R | A |
| Départ M2 / M3 | 0x3900 / 0x4900 | 2 | 10 | | R | A, si le circuit existe |
| Ballon ECS (sonde de charge) filtrée | 0x0812 | 2 | 10 | | R | A |
| ECS sortie (sonde 5B) | 0x0814 | 2 | 10 | | R | A |
| Consigne ECS effective | 0x6500 | 2 | 10 | | R | A |
| Fumées filtrée | 0x0816 | 2 | 10 | | R | A |
| Ambiante A1M1 (si commande à distance avec sonde) | 0x0896 | 2 | 10 | | R | A |
| Retour (capteur de débit) | 0x0C20 | 2 | 100 | | R | C |

## Brûleur

| Nom | Adr. | Oct. | div | R/W | Conf. |
|---|---|---|---|---|---|
| Flamme (0 = éteint) | 0x55D3 | 1 | 1 | R | A |
| Signal de flamme (brut) | 0x55DD | 1 | 1 | R | B |
| Puissance instantanée | 0xA38F | 1 | ÷ 2 | R | A |
| Taux de modulation | 0xA305 | 1 | ÷ 2 | R | A |
| Démarrages | 0x088A | 4 | 1 | R (W = remise à zéro) | A |
| Heures de fonctionnement (en secondes) | 0x08A7 | 4 | 3600 | R | A |
| Défaut du boîtier de commande brûleur | 0x5738 | 1 | 1 | R | A |

## Pompes et vanne

| Nom | Adr. | Oct. | R/W | Conf. |
|---|---|---|---|---|
| Pompe interne | 0x7660 | 1 | R | A |
| Pompe de circuit A1M1 | 0x2906 | 1 | R | A |
| Pompe de charge ECS | 0x6513 | 1 | R | A |
| Pompe de bouclage | 0x6515 | 1 | R | A |
| État de la charge ECS (0 inactive / 1 en charge / 2 post-circulation) | 0x650A | 1 | R | A |
| Vanne 3 voies (0..3) | 0x0A10 | 1 | R | A (signification des codes : B) |
| Vitesse pompe interne (%) | 0x0A3C | 1 | R | B |

## Modes, consignes, courbe

| Nom | Adr. | Oct. | div | Plage | R/W | Conf. |
|---|---|---|---|---|---|---|
| Mode A1M1 | 0x2323 | 1 | 1 | 0 arrêt, 1 ECS, 2 chauffage + ECS, 3 réduit permanent, 4 normal permanent | R/W | A |
| Régime actuel A1M1 | 0x2500 | 1 | 1 | 0 arrêt, 1 réduit, 2 normal, 3 normal permanent | R | A |
| Consigne ambiante normale | 0x2306 | 1 | 1 | 3..37 °C | R/W | A (vérifiée) |
| Consigne ambiante réduite | 0x2307 | 1 | 1 | 3..37 °C | R/W | A |
| Consigne party | 0x2308 | 1 | 1 | 4..37 °C | R/W | A |
| Consigne ambiante externe (0 = celle de la régulation) | 0x2321 | 1 | 1 | 0..37 °C | R/W | A |
| Consigne ECS | 0x6300 | 1 | 1 | 10..60 °C | R/W | A |
| Éco / party (lecture) | 0x2302 / 0x2303 | 1 | 1 | 0/1 | R officiellement | conflit |
| État éco / party | 0x2331 / 0x2330 | 1 | 1 | 0/1 | R/W | A |
| Durée max party (codage F2) | 0x27F2 | 1 | 1 | 0..12 h | R/W | A |
| Pente de la courbe A1 | 0x27D3 | 1 | 10 | 0,2..3,5 | R/W | A |
| Niveau de la courbe A1 | 0x27D4 | 1 | 1 | −13..40 K, signé | R/W (**lecture seule ici**) | A |
| Charge ECS unique | 0x65F5 | 1 | 1 | 0/1 | R/W | A si `_200_11` |

## Programmes, vacances, horloge

| Nom | Adr. | Oct. | Conf. |
|---|---|---|---|
| Programme chauffage A1M1 | 0x2000 | 56 (`DAY_SCHEDULE`) | B |
| Programme ECS A1M1 | 0x2100 | 56 | B |
| Programme bouclage A1M1 | 0x2200 | 56 | B/C |
| Vacances actives | 0x2535 | 1 | A |
| Début / fin des vacances | 0x2309 / 0x2311 | 8 (BCD) | A (écriture non supportée) |
| Date et heure | 0x088E | 8 (BCD) | A |

## Défauts et diagnostic

| Nom | Adr. | Oct. | Conf. |
|---|---|---|---|
| Défaut collectif | 0x0A82 | 1 | A |
| Historique des défauts 1..20 | 0x7590 + 9 × n | 9 (code + horodatage BCD), ou 1 pour le code seul | A |
| États des sondes (0 OK … 6 absente) | 0x083A ext., 0x083B chaud., 0x083E fumées | 1 | A |
| Compteurs de gaz, année en cours (chauffage / ECS) | 0x9128 / 0x925C | 4 | C |
| **Pression de l'installation** | — | — | **n'existe pas** (cf. `pression-circuit-chauffage.md`) |

## Adresses à ne pas utiliser (mauvaises sources)

| Fausse adresse | Bonne adresse | Remarque |
|---|---|---|
| 0x0845 / 0x0846 (pompes ECS) | 0x6513 / 0x6515 | famille KW (fioul) |
| 0x0847 (défaut collectif) | 0x0A82 | famille KW |
| 0x0842 (brûleur) | 0x55D3 | 0x0842 = relais K12 sur 20CB |
| 0x2305 / 0x2304 (courbe) | 0x27D3 / 0x27D4 | « 0x2305 war falsches Register » (openv) |
| 0x7507… (historique défauts) | 0x7590… | bloque le dialogue sur 20CB |

## Comportement du composant (PR #4453)

| Point | Comportement |
|---|---|
| `div_ratio` | uniquement 1, 10, 100, 1000 ou 3600 ; le ÷ 2 se fait par le filtre `multiply: 0.5` |
| 2 octets, `div_ratio` 10 ou 100 | décodé en int16 signé : températures négatives correctes |
| 1 octet, `div_ratio: 1` | non signé ; signé par le filtre `lambda` |
| `number` négatif | l'écriture est un comportement indéfini en C++ : **ne jamais écrire de valeur négative** |
| Longueur maximale | 9 octets (VitoWiFi) |
| `update_interval` | 10 s par défaut, 1 à 1800 s ; à fixer sur chaque entité |
| `binary_sensor` | 1 octet, toute valeur ≠ 0 = ON |

## Limites

- **Débit** : 4800 bauds, une requête à la fois, la régulation répond en 0,2 à 3 s. Viser moins de 0,5 requête/s, avec des intervalles décalés (nombres premiers) pour éviter les rafales. L'entité `QUEUE_SIZE` surveille la saturation.
- **Mémoire de l'ESP8266** : rester autour de 30–35 entités, pas de `web_server`, peu de RAW de 9 octets ou de `DAY_SCHEDULE`.
- **Écritures** : les consignes et les modes sont stockés en EEPROM. On écrit seulement quand une valeur change, **jamais en boucle** (pas de régulation PID qui écrit chaque minute). Ne jamais écrire :
  - les codages (0x27xx hors D3/D4/F2, 0x57xx, 0x67xx, 0x77xx) ;
  - les variables LON `nvi*` (0xA38x, 0xA3Cx) ;
  - 0x7500 (test des relais) ;
  - les compteurs ;
  - l'horloge.

## Sources

- Liste officielle Vitogate 200, 20CB HO1B : https://www.viessmann-community.com/viessmann/attachments/viessmann/customers-heatpump-hybrid/45475/1/vitogate_200_typ_knx-Datenpunktliste.pdf
- Export de la base Vitosoft : https://github.com/philippoo66/optolink-splitter/wiki/310-Parameter-Addresses
- ViessData21 : https://github.com/philippoo66/ViessData21 ; discussion #4 : https://github.com/philippoo66/ViessData21/discussions/4
- Discussion openv #603 : https://github.com/openv/openv/discussions/603 ; wiki openv : https://github.com/openv/openv/wiki/Adressen
- vcontrold : https://github.com/openv/vcontrold/tree/master/xml/300
- smarthomeNG `vscotho1_200_11` : https://github.com/smarthomeNG/plugins/blob/develop/viessmann/models/vscotho1_200_11.py
- PR ESPHome #4453 : https://github.com/esphome/esphome/pull/4453 ; VitoWiFi v1 : https://github.com/bertmelis/VitoWiFi/tree/v1/src
