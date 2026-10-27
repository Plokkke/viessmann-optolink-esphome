# Architecture et contrat d'interface

## Rôles

| Niveau | Projet | Rôle |
|---|---|---|
| Pièce | régulation (autre projet) | tête thermostatique Sonoff + sonde, consigne et planning propres à chaque pièce |
| Maison | régulation (autre projet), automatisation HA | agrège la demande des pièces, décide si la chaudière chauffe |
| Chaudière | **ce projet** | expose la Vitotronic dans HA par l'Optolink ; la Vitotronic choisit la température d'eau (courbe extérieure) et module le brûleur |

Ce projet ne contient aucune automatisation HA.

## Demande de chauffe (côté régulation)

- **DÉCIDÉ** : la chaudière chauffe dès qu'**au moins une tête chauffe** (`hvac_action: heating`).
- Plus tard, avec les sondes de pièce : besoin = `max(consigne − température)` sur les pièces. On n'envoie jamais une température brute, car les consignes diffèrent d'une pièce à l'autre.

## Entités à piloter

| Besoin | Entité | Valeur |
|---|---|---|
| Chauffer | `select` Operation mode | `Permanently normal` (4) |
| Ne pas chauffer (ECS seule) | `select` Operation mode | `Only hot water` (1) |
| Fonctionnement autonome (programme de la Vitotronic) | `select` Operation mode | `Heating and hot water` (2) |
| Niveau de chauffe (étape 2, à valider) | consigne ambiante externe `0x2321` | lecture seule pour l'instant ; à n'écrire qu'après avoir vérifié qu'elle n'est pas stockée en EEPROM |
| Température d'eau | `number` Heating curve slope, Room Temperature Setpoint | réglage initial, pas en continu |

## Contraintes

- **EEPROM** : les modes et les consignes sont stockés en EEPROM, qui s'use à chaque écriture. On écrit seulement quand la valeur change, au plus **une bascule toutes les 15–20 min**, et **jamais** en boucle.
- **Interdit** : les codages (`0x27xx` hors pente et niveau de courbe, `0x57xx`…), les compteurs, l'horloge, le test des relais. Voir `datapoints-optolink.md`.
- **Débit Optolink** : une requête à la fois ; les écritures passent dans la même file que les lectures.

## Sécurité (firmware)

Si HA est injoignable pendant **30 min** (depuis le démarrage ou depuis la dernière déconnexion), la carte repasse le mode à `Heating and hot water` : la Vitotronic reprend son propre programme horaire. `api.reboot_timeout` est désactivé pour que l'ESP ne redémarre pas en boucle sans HA.

## Commande à distance (codage A0)

- **DÉCIDÉ** : pas de commande à distance sur le bus KM, codage `A0:0`.
- Tant que le Tado est branché sur le bus KM (bornier 145), la régulation détecte une Vitotrol 300 et repasse d'elle-même à `A0:2`. Le jour du changement : débrancher le Tado, passer `A0` à 0 (sur l'écran, ou en écriture ponctuelle sur `0x27A0`), acquitter le défaut `bC`.
- L'entité A0 est en lecture seule dans le firmware.

## Alimentation

- Carte dédiée (`hardware/`) : HLK-PM01 (230 V → 5 V, 3 W) sur la carte, protégé par un fusible TR5 T1A (valeur Hi-Link) et une varistance Bourns MOV-07D431K, branché sur la fiche **96** par un bornier à vis Kefa KF128 ; chaque pièce porte sa référence LCSC dans le schéma ; remplace le bloc RPDZN5W6 du prototype.
- **DÉCIDÉ** : carte parallèle à la façade de la chaudière, flottante dans la partie élargie du boîtier ; **tête optique déportée** (LED IR et phototransistor enfoncés dans les trous de 3 mm de la fiche, reliés à la carte par une nappe 4 fils), ce qui découple l'enfichage de la position de la carte.
- **DÉCIDÉ** : tout est démontable : C3 sur barrettes femelles CMS (entraxe 15,24 mm), tête optique sur une embase JST PH 4 broches avec une nappe toute faite, 230 V sur bornier à vis, fusible sur porte-fusible TR5. Tout est traversant et soudé à la main, sauf les deux barrettes du C3 (CMS, éventuellement posées par JLCPCB). Pas de plan de masse. Carte en U renversé : 230 V sur la jambe gauche, fiche de la tête optique au centre, C3 sur la jambe droite.
- Prototype : bloc AC/DC 5 V 1 A (RPDZN5W6, sortie fixe), branché sur la fiche **96** de la régulation : sortie 230 V réservée aux accessoires, commandée par l'interrupteur de la chaudière, 6 A au total pour tous les accessoires (notice de montage p. 24-25).
- La sortie 5 V va sur `5V`/`GND` de l'ESP32-C3 super mini, dont le régulateur fournit le 3,3 V de l'adaptateur IR.
