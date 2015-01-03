#Conclusion

L'objectif est atteint :
    
* Les fonctionnalité voulues tiennent dans un fichier python de 250 lignes
* Montée en compétence sur gatling pour faire les tests

Des tests de performance en mode flask pur ont montré qu'il est possible de faire tourner une journée type en une heure :
 
* check and update unitaires: ~8000 en une heure, 2 par seconde pendant 20 minutes, 5 par secondes pendant 10 minutes le tout deux fois, afin de reproduire les pics de charge du midi et du soir.
* 200 insertion en 4 secondes toutes les 5 minutes
* 1 check en masse toutes les 15 secondes
* 3 transferts d'activité pendant le test
* Une réappro pendant le test

Cependant les conditions ne sont pas des conditions réelles
    
* La base mongo, le serveur ainsi que gatling sont sur la même machine, donc pas de temps réseau
* Il n'y a pas de réplica, donc pas de WriteConcern dans les écriture en base. Certaines options choisies pourraient ralentir les accès bases

Des tests ont été refait en mettant Flask derrière un serveur [Tornado](http://www.tornadoweb.org/en/stable/). Les charges ont été multipliées par deux. La charge tient toujours. On note 43 KO ("Connection refused") lors des 400 premières insertion en 4 secondes. Je mets ça sur le compte du temps de chauffage.

Les résultats des tirs de perf gatling sont dans le répertoire gatling/resultats.