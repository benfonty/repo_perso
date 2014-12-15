Serveur REST de gestion de stock SAV de téléphonie mobile en boutique.

Ecrit de manière à être le plus petit possible (actuellement 250 lignes).

Capable de faire du transfert de stock et du calcul de réapprovisionnement.

Utilise mongoDB pour le stockage, et Flask-restful pour le serveur.

L'objectif est de faire un tir de perf au moyen de gatling.

## Ce qu'il faudrait faire

Les tests ont été faits avec une seule instance de Mongo. Dans le cas de replica il faudrait adapter les WriteConcern au cas par cas.

Il n'y a pas de gestion d'authentification