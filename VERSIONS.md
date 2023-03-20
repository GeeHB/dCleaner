# *dCleaner* informations de version

#### Limitations connues

* sous Windows pas de multi-partitions

#### Dépendances

* Tout les OS (cf. ./README.md) 
  * python-psutil
  * alive_progress

#### Version 0.6.1

* xxx mars 2023
* Corrections 
  * BUG: absence de traitement en mode "log"
  * BUG: Affichages erronés en mode "log"
  * BUG: Decompte eroné du nombre de paramètres en ligne de commandes
  * BUG : alive_bar n'est pas importé si mode "log" 

#### Version 0.5.5

* 9 mars 2023
* "VERSION" devient "VERSIONS.md"
* Corrections 
  * Affichages en mode log
  * bug divers
  * **cmdLineParser.py** : un paramètre peut-être un float, un float négatif, eniter, chaîne, etc ....
* Ajouts 
  * paramètres *\-waitFiles* & *\-waitTasks* pour l'attente entre 2 fichiers et/ou traitements

#### Version 0.5.4

* 8 mars 2023
* Mise à jour de README.md
* Modification de l'entête des fichiers
* Ne peut être lancé par root !
* Suppression des fichiers et dossiers avec renommage
* Corrections 
  * corrections diverses
  * Bug : paramètres "-folder" non fonctionnel
  * Bug : -depth -1 (acceptation de valeurs numériques négatives dans la ligne de commandes)
  * Vérification du typage des paramètres (string attendus ?)
* %trash% peut se transformer en +sieurs dossiers 
  * on ne peut plus nettoyer individuellement des sous-dossier de %trash%
  * certains dossiers (dont ceux de %trash% et '~') ne peuvent être supprimés

#### Version 0.5.3

* 3 mars 2023
* l'option "-clean" accepte plusieurs dossiers séparés par ";" 
  * la chaîne %trash%  est remplacée par le chemin vers la corbeille de l'utilisateur appellant


* Utilisation de la librairie 'alive_progress' en remplacement des affichages du mode 'verbeux' 
  * ajout / supression de fichiers
  * vidage du dossier de padding

#### Version 0.5.2

* 27 janvier 2023
* ajout de l'option -clean {folder} pour cibler le nettoyage à un dossier (qui sera vidé puis supprimé) 
  * ajout de l'objet basicFolder dont héritera paddingFolder
* ajout de l'option -np : No Padding - Pas de "salissage" de la partition (par défaut False ...)

#### Version 0.4.1

* 29 dec. 2022
* 'sharedTools' est incorporé au projet comme sous-dossier
* Corrections mineures

#### Version 0.3.9

* 26 janv. 2022


* Corrections mineures 
  * Bug d'affichage avec l'option -clear
  * Gestion de la ligne de commandes
  * Gestion des cas d'erreur
  * Affichages 
    * Affiche "Attente" avant d'afficher le # de l'itération
* Affichage de la date de release
* Choix aléatoire du fichier lors de la suppression (meilleur pour le salissage de la partition)

#### Version 0.3.5

* 15 oct. 2021


* Corrections 
  * Si un seul mauvais param; en ligne de commmande 
    * utilisation de sharedTools v1.4.2


  * Le dossier est, par défaut, caché
  * Affichages
* Ajout du paramètre -? et/ou -help pour afficher la ligne de commande

#### Version 0.3.4

* 8 octobre 2021


* Modification des affichages 
  * Taille de la partition et taux de remplissage réel
  * Corrections mineures

#### Version 0.3.2

* 27 sept. 2021


* Utilisation des modules sharedTools (à la place des fichiers dans le dossier)
* Test(s) & corrections pour Windows
* Possibilité de founir +sieurs dossiers (séparés par "," ou "*" pour Windows)
* Logs plus efficaces
* Tous les paramètres peuvent être passés en ligne de commande (ajout des délais inter-traitements)
* Corrections 
  * bug lorsque le dossier de padding n'existe pas

#### Version 0.2.5

* 21 septembre 2021
* Corrections mineures 
  * bug d'affichage en mode logs
  * valeurs par défaut

#### Version 0.2.4

* 20 septembre 2021
* Corrections mineures 
  * Moins d'accès disque (optimisations)
  * Valeur(s) par défaut pour les paramètres de la ligne de commandes 
    * dossier par défaut selon l'OS


  * Attente entre 2 tâches


  * Affichage du mode d'execution ('adjust' et/ou 'cleaner')
  * Affichage de la suppression lorsque la taille du fichier est > au quota
* Ajout de l'option -clear pour supprimer le contenu du dossier de 'padding'
* Ajout de parameters.py 
  * Gestion des constantes communes
  * Gestion de la ligne de commande
* Nouvel algo pour déterminer la taille (aléatoire) d'un fichier (50% en ko / 50% en Mo)
* Modification des affichages (plus courts en mode logs + datés)
* Gestion de la ligne de commandes 
  * Aucun paramètre n'est obligatoire

#### Version 0.2.1

* 31 aout 2021
* Version complète (paramètres d'execution constants)

#### Version 0.1.1

* Mai 2020 - Version fonctionnelle (mais basique ...)