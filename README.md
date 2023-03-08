# *dCleaner* - Outil de nettoyage des partitions

## Présentation

`dCleaner` est un utilitaire en ligne de commande qui permet de nettoyer une partition disque. Il s'agit de saturer ponctuellement l'espace disponible avec des données aléatoire puis de libérer l'espace nouvellement utilisé. De la sorte, le contenu des fichiers effacés est automatiquement écrasé et ne pourra pas être récupéré par un logiciel espion.

En réalité, lorsqu'un fichier est "effacé , l'ensemble de ses données sont conservées sur le disque dur. L'objectif de cet utilitaire consiste à remplir le disque avec des données aléatoires afin d'effacer le contenu des fichiers précédement 'effacés'.

Une partition disque peut être découpée en 3 zones :

* L'espace effectivement utilisé par l'ensemble des fichiers du système;
* Une zone de remplissage - zone de *padding* - qui contient des fichiers aléatoires qui saturent artificiellement l'espace de stockage
* enfin l'espace libre de la partition. Le logiciel intervient dans la zone de *padding* qui permet de maintenir l'espace libre à la taille souhaitée puis ponctuellement dans la zone libre qui sera saturée - à un taux paramétrable - de fichiers qui seront à leur tour effacés.

> Plus l'espace libre sera ténu, et plus le taux de remplissage ponctuel de cette zone sera élevé et plus le disque sera protégé.

En plus de la saturation du disque dur, `dCleaner` peut être utilisé pour nettoyer un ou plusieurs dossiers. Dans ce cas, le contenu des fichiers sera remplacé par une séquence de caractères aléatoires puis le fichier sera effacé. Les noms des fichiers et des sous-dossiers concernés par l'opération seront aussi générés aléatoirement afin d'effacer efficacement leur trace. 
 
## Version

|Dépôt |https://coffee.cd03.fr/JHB/dCleaner| 
|---|---|
| **Date** | 8 mars 2023| | **Auteur** | JHB - [henry-barnaudiere.j@allier.fr](mailto:henry-barnaudiere.j@allier.fr)|
| **Version stable** | **0\.5.4 - branche** `master`| |**Version en cours** |xxx|  
|**Dépendances** |Python 3.xx |
|| alive_progress de rsalmei (pip install alive-progress) - doc : https://github.com/rsalmei/alive-progress
| | python-psutil (apt-get install python-psutil ou dnf install python-psutil) |
|**Testé sur**| *Linux* / *MacOS* - *Windows* à confirmer|


## Appel

### Ligne de commande

> Attention : le paramètre `depth` s'applique à tous les dossiers concernés par l'appel. Si plusieurs dossiers doivent bénéficier d'une profondeur spécifique, il sera nécessaire d'avoir autant d'appel de `dCleaner` que de dossiers.

### Exemples d'appels

-depth = -1 (defaut) => pas de suppression des (sous-)dossiers
= 0 => suppression du dossier et des sous-dossiers
= 1 => suppression des sous-dossiers à partir des sous-dossiers fils

* Lancement d'un nettoyage simple de la partition (avec les valeurs par défaut):
~~~
./dCleaner.py 
~~~

* Nettoyage intense (5 itérations) avec remplissage de la partition à 80% :
~~~
./dCleaner.py -fill 80 -i 5
~~~

* Suppression du contenu du dossier `~/temp` et de la poubelle avec tous leurs sous-dossiers (mais conservation des dossiers) :
~~~
./dCleaner.py -np -clear "~/temp;%trash%" -depth 1
~~~

### Automatisation

Le script est destiné à être appelé mais surtout à être lancé régulièrement par un gestionnaire de tâches planifiées.

Si l'on souhaite récurer des logs, on peut utiliser le commutateur `-log` afin d'indiquer à l'utilitaire de ne pas mettre en forme (colorisation, gras, etc...) les affichages et d'être un peu moins verbeux.

Dans l'exemple suivant trois tâches `cron` sont lancées regulièrement : une pour s'assurer que la partition ne staure pas et une seconde pour nettoyer la partition, une troisième permet de nettoyer quotidiennement la poubelle ainsi que le dossier des téléchargements.

```
# >>>
# >>>
#
# JHB - Nettoyage auto. de la partition
#
#       - Simulation d'un taux de remplissage de 75%
#       - Toutes les 30 min. on s'assure que l'on ne sature pas la partition
#       - Toutes les 2 heures la partition est à nouveau nettoyée à hauteur de 30% de ce qui reste de libre
#       - Tous les jours à minuit la poubelle et le dossier de téléchargements sont vidés de leur contenu
#

# Vérification périodique que le dossier de 'padding' n'est pas trop volumineux
0,30 * * * * /etc/scripts/dCleaner/dCleaner.py -fill 75 -log -adjust >> /var/log/dCleaner.log

# Nettoyages quotidiens de la partition courante (3 itérations)
15 */2 * * * /etc/scripts/dCleaner/dCleaner.py -fill 75 -i 3 -log >> /var/log/dCleaner.log

# Effacement quotidien du dossier téléchargement et de la poubelle (on ne touche pas aux dossiers)
* 0 * * * /etc/scripts/dCleaner.py -np -clean "~/Téléchargements;%trash%" -depth 1 >> /var/log/dCleaner.log

#
# <<<
# <<<
```