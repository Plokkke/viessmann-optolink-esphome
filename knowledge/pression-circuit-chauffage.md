# Pression du circuit de chauffage — Vitodens 222-W B2LA

Références : notice de montage et de maintenance B2LA (`manuals/vitodens-222-w-b2la-notice-montage-maintenance-fr.pdf`, « notice »), notice d'utilisation HO1B (`manuals/vitotronic-200-ho1b-notice-utilisation-fr.pdf`, « notice utilisateur »), Planungsanleitung (`manuals/vitodens-200-w-222-w-300-w-planungsanleitung-de.pdf`).

## Détection, pilotage, correction

| Question | Réponse |
|---|---|
| La chaudière mesure-t-elle la pression ? | **Non** : manomètre à aiguille 0–4 bar uniquement (notice utilisateur p. 21 ; pièce 0014). La platine A1 a une entrée « aND sonde de pression d'eau » (notice p. 179), absente de la liste des pièces et des fonctions : non équipée sur le B2LA |
| Lisible par Optolink ? | **Non** : aucun datapoint de pression connu pour `20CB` |
| Code défaut « pression basse » ? | **Non**. Symptômes indirects : **F2** (limiteur de sécurité, p. 142) et **F1** (limiteur fumées, p. 141), dont la première mesure est « contrôler le niveau de remplissage, purger » |
| Correction automatique ? | **Non** : ni électrovanne de remplissage ni accessoire Viessmann. Possible seulement avec un remplisseur tiers (Reflex Fillcontrol, Caleffi…) posé par un pro avec disconnecteur EN 1717 |
| Surveillance à distance ? | Capteur externe : transducteur 0–4 bar (sortie 0,5–4,5 V) sur un raccord du circuit, lu par l'ESP (entrée `A0` du D1 mini, via un pont diviseur) |

## Valeurs de référence

| Paramètre | Valeur | Source |
|---|---|---|
| Pression minimale | > 1,0 bar | notice p. 35, notice utilisateur p. 21 |
| Pression à froid visée | prégonflage du vase + 0,1 à 0,2 bar → **1,0 à 1,5 bar** | notice p. 58 |
| Vase d'expansion intégré | 10 l, prégonflage d'usine **0,8 bar** | Planung p. 16, notice p. 58 |
| Soupape de sécurité | **3 bar** | pièce 0029 |
| Pendant la purge de la chaudière | ≤ 1,5 bar | notice p. 40 |
| À chaud | non donné par le manuel ; usage : + 0,3 à 0,6 bar, rester sous ~2,5 bar | — |

## Procédure de remplissage manuel (notice p. 35–42)

1. Couper la chaudière et laisser refroidir (pas de vidange au-dessus de 40 °C, p. 147).
2. Fermer le gaz ; ouvrir les vannes d'arrêt départ et retour chauffage (sous la chaudière, p. 35).
3. Si la régulation est sous tension : **OK + menu 4 s** → « Fonction de maintenance » → **« Remplissage »** (vanne d'inversion en position médiane, p. 36).
4. Raccorder un flexible d'eau froide (de préférence avec disconnecteur), purgé de son air, au **robinet de remplissage/vidange A** sous la chaudière ; remplir jusqu'à **1,2–1,5 bar** à froid.
5. Fermer le robinet A, débrancher le flexible.
6. Air dans la chaudière (p. 39–40) : fermer les vannes d'arrêt, retirer la tôle de protection, flexible fourni sur le purgeur supérieur vers l'égout, ouvrir remplissage et purge jusqu'à disparition du bruit d'air (≤ 1,5 bar), fermer la purge puis le remplissage, rouvrir les vannes. **Jamais par la soupape de sécurité.**
7. Purge de l'installation (p. 41–42) : gaz fermé, régulation en marche, purgeur rapide de la pompe ouvert ; **OK + menu 4 s** → « Fonctions de maintenance » → **« Purge d'air »** (20 min, brûleur coupé) ; purger les radiateurs.
8. Réajuster la pression (elle baisse après la purge), rouvrir le gaz, remettre en service, contrôler à chaud.
9. Tous les 6 mois : manœuvrer légèrement la soupape de sécurité (notice utilisateur p. 41).

## Diagnostic

| Symptôme | Cause probable |
|---|---|
| Baisse lente, pas de fuite visible | soupape qui goutte (vérifier son évacuation), purgeur rapide, air évacué après un remplissage |
| Forte amplitude froid/chaud, soupape qui s'ouvre à chaud | **vase d'expansion dégonflé** ou membrane percée (de l'eau à la valve du vase = membrane percée) : contrôle du prégonflage à faire par un installateur (p. 58) |
| Baisse avec traces d'eau | fuite réseau : raccords, radiateurs, vannes, robinet de vidange |
| Hausse lente | robinet de remplissage A pas étanche |
| Hausse après puisage d'eau chaude | **échangeur à plaques ECS percé** : l'eau sanitaire (3–6 bar) passe dans le chauffage |

Le suivi de la pression dans le temps (capteur externe ou relevé manuel) départage ces causes : une courbe qui suit la température pointe le vase, une courbe qui suit les puisages pointe l'échangeur.
