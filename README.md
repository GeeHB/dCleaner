# Nettoyage des partitions
## Présentation
`dCleaner` est un utilitaire en ligne de commande qui permet de nettoyer une partition disque. Il s'agit de saturer ponctuellement l'espace disponible avec des données aléatoire puis de libérer l'espace nouvellement utilisé. De la sorte, le contenu des fichiers effacés est automatiquement écrasé et ne pourra pas être récupéré par un logiciel espion.

Lorsqu'un fichier est "effacé , en réalité l'ensemble de ses données sont conservées sur le disque dur. L'objectif de cet utilitaire et de remplir le disque avec des données aléatoire afin d'effacer le contenu des fichiers prétendument effacés.

Comme le montre le schéma suivant, une partition disque peut être découpée en 3 zones :
* L'espace effectivement utilisé par l'ensemble des fichiers du système;
* Une zone de remplissage - zone de *padding* - qui contient des fichier aléatoire et sature artificiellement l'espace de stockage
* enfin l'espace libre de la partition. 
Le logiciel intervient dans la zone de *padding* qui permet de maintenir l'espace libre à la taille souhaitée puis ponctuellement dans la zone libre qui sera saturée - à un taux paramétrable - de fichiers qui seront à leur tour effacés.

> Plus l'espace libre sera ténu, et plus le taux de remplissage ponctuel de cette zone sera élevé et donc plus le disque sera protégé des récupérations indues.

## Version
|Dépôt |https://coffee.cd03.fr/JHB/dCleaner|
|---|---|
| **Date** |  06 décembre 2021|
| **Auteur** |  JHB - <henry-barnaudiere.j@allier.fr>|
| **Version stable** |  **0.3.8 - branche `master`**|
|**Version en cours** |xxx|  
|**Dépendances** |Python 3.xx|
|**Testé sur**| *Linux* / *MacOS* - *Windows* à confirmer|
## Appel
### Ligne de commande
### Automatisation
Le script est destiné à être appelé mais surtout à être lancé régulièrement par un gestionnaire de tâches planifiées.

Si l'on souhaite récurer des logs, on peut utiliser le commutateur `-log` afin d'indiquer à l'utilitaire de ne pas mettre en forme (colorisation, gras, etc...) les affichages et d'être un peu moins verbeux. 

Dans l'exemple suivant deux tâches `cron` sont lancées regulièrement : une pour s'assurer que la partition ne staure pas et une seconde pour nettoyer la partition.

~~~ bash
# >>>
# >>>
#
# JHB - Nettoyage auto. de la partition
#
#       - Simulation d'un taux de remplissage de 75%
#       - Toutes les 30 min. on s'assure que l'on ne sature pas la partition
#       - Toutes les 2 heures la partition est à nouveau nettoyée à hauteur de 30% de ce qui reste de libre
#

# Vérification périodique que le dossier de 'padding' n'est pas trop volumineux
0,30 * * * * /etc/scripts/dCleaner/dCleaner.py -fill 75 -log -adjust >> /var/log/dCleaner.log
# Nettoyages quotidiens de la partition courante (3 itérations)
15 */2 * * * /etc/scripts/dCleaner/dCleaner.py -folder -fill 75 -i 3 -log >> /var/log/dCleaner.log
#
# <<<
# <<<
~~~