## But

LE but de ce projet était d'exploiter les données géographiques issues de http://www.geonames.org/ afin de trouver le lieu habité dans le monde qui se trouve le plus loin possible d'un autre lieu habité.

## Moyen

Charger les données dans une base MongoDB puis utiliser la recherche géodsatiale de MongoDB pour trouver pour chaque lieu le lieu le plus proche (avec la distance).

Ensuite il suffit de trier par distance.

## Résultat

D'après les données, l'endroit peuplé sur terre qui se trouve le plus loin de tous les endroits peuplé sur terre est "McMurdo Station" (158.86299,-54.61383) dans le "British Antarctic Territory", qui se trouve à 2604 kilomètres de la "ville" la plus proche, à savoir "Macquarie Island" (168.12927, -46.89962) dans les "Coral Sea Islands".
Talonné de près par "Edinburgh of the Seven Seas", "Saint Helena" (-12.31155, -37.06757) qui se trouve à 2434 km de "Barren Ground", "Saint Helena" (-5.75,-15.98028)