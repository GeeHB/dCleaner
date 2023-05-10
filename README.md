# *dCleaner* - Outil de nettoyage des partitions

## Présentation

`dCleaner` est un utilitaire en ligne de commande qui permet de nettoyer une partition disque et de s'assurer que les fichiers effacés ne pourront pas être récupérés par une application tierce. Pour cela il s'agit de saturer ponctuellement l'espace disponible avec des données aléatoires puis de libérer l'espace nouvellement utilisé. De la sorte, le contenu des fichiers effacés est automatiquement écrasé et ne pourra pas être récupéré par un logiciel espion.

En réalité, lorsqu'un fichier est "effacé, ses données sont conservées sur le disque dur seul l'accès étant supprimé. L'objectif de cet utilitaire consiste à remplir le disque avec des données aléatoires afin d'effacer factuellement le contenu des fichiers précédemment 'effacés'.

Pour et utilitaire une partition disque peut être découpée en 3 zones :

* L'espace effectivement utilisé par l'ensemble des fichiers du système;
* une zone de remplissage - zone de *padding* - qui contient des fichiers aléatoires qui saturent artificiellement l'espace de stockage;
* puis l'espace libre de la partition.

Le logiciel intervient dans la zone de *padding* qui permet de maintenir l'espace libre à la taille souhaitée puis ponctuellement dans la zone libre qui sera saturée de fichiers - à un taux paramétrable - puis qui seront à leur tour effacés.

> Plus l'espace libre sera ténu et plus le taux de remplissage ponctuel de cette zone sera élevé et donc plus le disque sera protégé.

En plus de la saturation du disque dur, `dCleaner` peut être utilisé pour nettoyer un ou plusieurs dossiers. Dans ce cas, le contenu des fichiers sera remplacé par une séquence de caractères aléatoires puis le fichier sera effacé. Les noms des fichiers et des sous-dossiers concernés par l'opération seront aussi générés aléatoirement afin d'effacer efficacement toutes leurs traces.

## Informations de version

| Dépôt | https://coffee.cd03.fr/JHB/dCleaner |
|-------|-------------------------------------|
| **Date** | 10 mai 2023 |
| **Version stable** | **0\.8.0 - branche** `master` |
| **Dépendances** | Python 3.xx |
|  | *facultatif:* alive_progress de rsalmei (pip install alive-progress) - doc : <https://github.com/rsalmei/alive-progress> |
|  | python-psutil (apt-get install python-psutil ou dnf install python-psutil) |
| **Testé sur** | *Linux (Fedora 37)* / *MacOS* - *Windows* à confirmer |

## Appel

### Ligne de commandes

`dCleaner` accepte différents paramètres passés en ligne de commandes. Un appel simple, sans aucun paramètre, entraine l'exécution du script avec toutes les valeurs par défaut.

Les différents paramètres sont définis comme suit :

| Paramètre court | Paramètre long | Valeur par défaut | Rôle |
|-----------|-----------|-------------------|------|
| *-h*  | *--help* |  | Affichage de l'aide |
|*-f* {dossier}  | *-folder* {dossier} | ~/.padding | Dossier utilisé pour le remplissage de la partition. Tous les fichiers générés seront crées dans ce dossier. |
| *-x* | *--clear* |  | Effacement du dossier de remplissage. Tous les fichiers seront automatiquement supprimés. Ce paramètre est utile lorsque l'on a besoin de libérer de la place sur la partition. |
| *-fi* {%} | *--fill* {%} | 80 | Taux de remplissage attendu pour la partition. |
| *-p* {%} | *--padding* {%} | 50 | Taux (en % de la taille libre) à nettoyer. Par exemple, s'il reste 70Go de libre dans la partition, un taux de 50% entrainera la génération de fichiers à hauteur de 35Go puis la suppression de 35Go de fichiers de remplissage. Tous les fichiers en question seront crées ou pris dans le dossier de remplissage. |
| *-a* | *--adjust*|  | Ajustement de la taille du dossier de remplissage. Cette option permet de s'assurer que le dossier de remplissage ne prend pas plus de place que demandé ou inversement qu'il n'est pas trop peu rempli. A défaut des fichiers sont supprimés ou ajoutés en fonction de la comparaison entre le taux de remplissage actuel et le taux demandé par le paramètre *-fill* |
| *-c* {dossiers} | *--clean* {dossiers} |  | Suppression du contenu des {dossiers}. Par exemple la suppression de 3 dossiers : -clean ~/mon_dossier /etc/temp %trash%|
|  |  |  | **Attention :** lorsqu'un dossier à la valeur *%trash%* il est remplacé par le chemin vers les différentes corbeilles de l'utilisateur appelant.|
| *-d* {value} | *--depth* {value} | *none* | Profondeur du nettoyage des dossiers. |
|  |  |  | = *none* (par défaut) : pas de suppression des sous-dossiers. |
|  |  |  | = 0 : suppression du dossier et de ses sous-dossiers. |
|  |  |  | = 1 : suppression des sous-dossiers à partir du dossier fils. |
|  |  |  | = {n} : suppression des sous-dossiers à partir de la profondeur {n} par rapport au dossier courant. |
|  |  |  | **Attention :** le paramètre `depth` s'applique à tous les dossiers concernés par l'appel. Si plusieurs dossiers doivent bénéficier d'une profondeur spécifique, il sera nécessaire d'avoir autant d'appel de `dCleaner.py` que de dossiers. |
| *-i* | *--iteration* | 1 | Nombre d'itération(s). Ce paramètre correspond à la fois au nombre d’occurrence du process de remplissage mais aussi au nombre de fopis ou les fichiers seront ré-écris en mode effacement des dossiers (paramètre *\-clean*). |
| *-nc* | *--nocolor* |  | mode "no color" : pas de colorisation des affichages. Utile pour la génération de fichiers de logs par exemple |
| *-np* | *--nopadding* |  | mode "no padding" : pas de remplissage de la partition |
| *-l* | *--log* |  | Mode moins verbeux à destination des fichiers de logs. Dans ce mode, les affichages et les notifications sont réduits aux strict minimum |
| *-wf* {value} | *--waitfiles* {value} | 0 | Delai d'attente en seconde entre 2 suppressions de fichiers. |
| *-wt* {value} | *--waittasks* {value} | 5 | Délai d'attentes en secondes entre deux itérations (paramètre *\-i* > 1) |

### Exemples d'appels

##### Lancement d'un nettoyage simple de la partition (avec les valeurs par défaut):

```
./dCleaner.py 
```

##### Nettoyage intense (5 itérations) avec remplissage de la partition à 80% :

```
./dCleaner.py --fill 80 --iteration 5
```
Equivalent à :
```
./dCleaner.py -fi 80 -i 5
```
##### Suppression du contenu du dossier `~/temp` et des dossiers poubelle avec tous leurs sous-dossiers mais conservation des dossiers racines :
```
./dCleaner.py --nopadding --clear ~/temp %trash% --depth 1
```
Equivalent à :
```
./dCleaner.py -np -c ~/temp %trash% -d 1
```
### Automatisation
Le script est destiné à être appelé mais surtout à être lancé régulièrement par le gestionnaire de tâches planifiées.

Si l'on souhaite récupérer des logs, on peut utiliser le commutateur `--log` / '-l' afin d'indiquer à l'utilitaire de ne pas mettre en forme les affichages (colorisation, gras, etc...) et d'être un peu moins verbeux.

Dans l'exemple suivant trois tâches `cron` sont lancées régulièrement : une pour s'assurer que la partition ne sature pas et une seconde pour nettoyer la partition, une troisième permet de nettoyer quotidiennement la poubelle ainsi que le dossier des téléchargements.

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
0,30 * * * * /etc/scripts/dCleaner/dCleaner.py -fi 75 -l -a >> /var/log/dCleaner.log

# Nettoyages quotidiens de la partition courante (3 itérations)
15 */2 * * * /etc/scripts/dCleaner/dCleaner.py -fi 75 -i 3 -l >> /var/log/dCleaner.log

# Effacement quotidien du dossier téléchargement et de la poubelle (on ne touche pas aux dossiers)
* 0 * * * /etc/scripts/dCleaner.py -np -c ~/Téléchargements %trash% -d 1 -l >> /var/log/dCleaner.log

#
# <<<
# <<<
```