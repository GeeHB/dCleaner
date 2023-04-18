# coding=UTF-8
#
#   Fichier     :   parameters.py
#
#   Auteur      :   JHB
#
#   Description :   Gestion de la ligne de commande et des constantes.
#

import argparse
from sharedTools import colorizer as color
from mountPoints import mountPointTrashes
import sys, os, platform

# Nom et version de l'application
APP_NAME = "dCleaner.py"
APP_CURRENT_VERSION = "0.7.1"
APP_RELEASE_DATE = "18-04-2023"

#
# Motif aléatoire
#

# Caractères utilisés pour l'encodage
PATTERN_BASE_STRING = "ABCDEFGKHIJLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/!=@&_-:;,?<>$"

# Taille d'un motif aléatoire en octets
PATTERN_MIN_LEN = 33
PATTERN_MAX_LEN = 5121

#
# Gestion des fichiers
#

# Nom du sous-dossier
DEF_FOLDER_NAME = ".padding"

DEF_WIN_ROOT_FOLDER = "c:\\"      # Dossiers par défaut
DEF_LINUX_ROOT_FOLDER = "~"

# Taille d'un fichier (en k ou M octets)
FILESIZE_MIN = 1
FILESIZE_MAX = 1024

#
# Dossiers à nettoyer
#
FOLDERS_TRASH = "%trash%"      # La poubelle de l'utilisateur

#
# Commandes / arguments reconnu(e)s (longues et courtes)
#

# Commutateurs
#

# Mode non verbeux (spécifique pour les fichiers de logs) - Par défaut Non
ARG_LOGMODE_S   = "-l"
ARG_LOGMODE     = "--log"
COMMENT_LOGMODE = "Mode non verbeux, pour les fichiers de logs"

# Pas de colorisation des sorties - Par défaut les sorties seront colorisées
ARG_NOCOLOR_S = "-nc"
ARG_NOCOLOR   = "--nocolor"
COMMENT_NOCOLOR = "Ne pas coloriser les affichages"

# Pas de remplissage (juste nettoyer ou effacer)
ARG_NOPADDING_S = "-np"
ARG_NOPADDING   = "--nopadding"
COMMENT_NOPADDING = "Pas de remplissage de la partition"

# Effectue uniquement la vérification du dossier de remplissage
ARG_ADJUST_S = "-a"
ARG_ADJUST   = "--adjust"
COMMENT_ADJUST = "Ajustement du dossier de remplissage"

# Nettoyage du dossier de padding
ARG_CLEAR_S = "-x"
ARG_CLEAR   = "--clear"
COMMENT_CLEAR = "Nettoyage du dossier de remplissage"

# Paramètres : {arg} {value}
#

# Dossier utilisé pour le remplissage (la partition associée sera saturée)
ARG_FOLDER_S = "-f"
ARG_FOLDER   = "--folder"
COMMENT_FOLDER = "Dossier de remplissage"

# Nettoyage de tous les fichiers et dossiers contenu dans le dossier source
ARG_CLEANFOLDER_S = "-c"
ARG_CLEANFOLDER   = "--clean"
COMMENT_CLEANFOLDER = "Nettoyage du ou des dossiers"

# Profondeur du nettoyage (et de l'effacement des dossiers)
ARG_DEPTH_S = "-d"
ARG_DEPTH   = "--depth"
COMMENT_DEPTH = "Profondeur des dossiers pour la suppression (à partir du dossier courant)"

DEF_DEPTH = None    # Par défaut pas de nettoyage en profondeur des dossiers (on ne supprime pas les sous-dossiers)
MIN__DEPTH      = 0
MAX_DEPTH       = 15

# Nombre d'itération à effectuer - Par défaut = 1
ARG_ITERATE_S = "-i"
ARG_ITERATE   = "--iteration"
COMMENT_ITERATE = "Nombre d'itération du process de nettoyage"

DEF_ITERATE = 1           # Nombre de fois ou sera lancé le processus de remplissage / nettoyage
MIN_ITERATE = 1
MAX_ITERATE = 10

# Pourcentage de la partition devant être plein (y compris de padding) - Par défaut 80%
ARG_FILLRATE_S = "-fi"
ARG_FILLRATE   = "--fill"
COMMENT_FILLRATE = "Taux de remplissage de la partition"

DEF_FILLRATE = 80    # Pourcentage de remplissage max. de la partition
MIN_FILLRATE = 1
MAX_FILLRATE = 95 

# Pourcentage restant de la partition à salir à chaque itération - Par défut 30%
ARG_PADDINGRATE_S = "-p"
ARG_PADDINGRATE   = "--padding"
#COMMENT_PADDINGRATE = "Taille (en pourcentage de la taille libre) à nettoyer"
COMMENT_PADDINGRATE = "Taille (en %% de la taille libre) à nettoyer"

DEF_PADDINGRATE = 30           # Dans le % restant, quelle est le taux de renouvellement (ie ce pourcentage sera nettoyé à chaque lancement)
MIN_PADDINGRATE = 1
MAX_PADDINGRATE = 50

# Attente entre le traitement de 2 fichiers
ARG_ELAPSEFILES_S = "-wf"
ARG_ELAPSEFILES   = "--waitfiles"
COMMENT_ELAPSEFILES = "Durée en s entre 2 suppressions de fichiers"

DEF_ELAPSEFILES = 0.1
MIN_ELAPSEFILES = 0.0
MAX_ELAPSEFILES = 180.0

# Attente entre 2 itérations
ARG_ELAPSETASKS_S = "-wt"
ARG_ELAPSETASKS   = "--waittasks"
COMMENT_ELAPSETASKS = "Durée en s entre 2 itérations"

DEF_ELAPSETASKS = 5.0
MIN_ELAPSETASKS = 5.0
MAX_ELAPSETASKS = 180.0
   
#
#   classe options : Gestion de la ligne de commande et des paramètres ou options
#
class options(object):

    # Construction
    #
    def __init__(self):

        # Valeurs par défaut
        self.color_ = None      # Outil de colorisation
        self.verbose_ = True    # Par défaut l'application trace tout ...
        
        self.adjust_ = False    # Par défaut tous les traitements sont effectués
        
        self.noPadding_ = False
        
        self.iterate_ = DEF_ITERATE
        
        self.fillRate_ = DEF_FILLRATE
        self.renewRate_ = DEF_PADDINGRATE
        self.clear_ = False

        self.waitFiles_ = MIN_ELAPSEFILES
        self.waitTasks_ = MIN_ELAPSETASKS
        
        self.clean_ = []        # Nettoyage d'un ou plusieurs dossiers
        self.cleanDepth_ = DEF_DEPTH   # Profondeur du nettoyage (pas de suppression)

        # Dossier par défaut
        self.folder_ = os.path.join(options.homeFolder(), DEF_FOLDER_NAME)   

    # Analyse de la ligne de commandes
    #   returne un booléen
    def parse(self):
        
        parser = argparse.ArgumentParser(epilog = self.version())
        
        parser.add_argument(ARG_LOGMODE_S, ARG_LOGMODE, action='store_true', help = COMMENT_LOGMODE, required = False)
        parser.add_argument(ARG_NOCOLOR_S, ARG_NOCOLOR, action='store_true', help = COMMENT_NOCOLOR, required = False)
        parser.add_argument(ARG_NOPADDING_S, ARG_NOPADDING, action='store_true', help = COMMENT_NOPADDING, required = False)
        
        # Arguments mutuellement exclusifs
        lancement = parser.add_mutually_exclusive_group()
        lancement.add_argument(ARG_CLEAR_S, ARG_CLEAR, action='store_true', help = COMMENT_CLEAR, required = False)
        lancement.add_argument(ARG_ADJUST_S, ARG_ADJUST, action='store_true', help = COMMENT_ADJUST, required = False)

        parser.add_argument(ARG_FOLDER_S, ARG_FOLDER, help = COMMENT_FOLDER, required = False, nargs=1)
        parser.add_argument(ARG_ITERATE_S, ARG_ITERATE, help = COMMENT_ITERATE, required = False, nargs=1, default = [DEF_ITERATE], type=int, choices=range(MIN_ITERATE, MAX_ITERATE + 1))
        parser.add_argument(ARG_FILLRATE_S, ARG_FILLRATE, help = COMMENT_FILLRATE, required = False, nargs=1, default = [DEF_FILLRATE], type=int)
        parser.add_argument(ARG_PADDINGRATE_S, ARG_PADDINGRATE, help = COMMENT_PADDINGRATE, required = False, nargs=1, default = [DEF_PADDINGRATE], type=int)
        parser.add_argument(ARG_DEPTH_S, ARG_DEPTH, help = COMMENT_DEPTH, required = False, nargs=1, type=int, choices=range(MIN__DEPTH, MAX_DEPTH + 1))
        parser.add_argument(ARG_CLEANFOLDER_S, ARG_CLEANFOLDER, help = COMMENT_CLEANFOLDER, required = False, nargs='+')

        parser.add_argument(ARG_ELAPSEFILES_S, ARG_ELAPSEFILES, help = COMMENT_ELAPSEFILES, required = False, nargs=1, default = [DEF_ELAPSEFILES], type=float)
        parser.add_argument(ARG_ELAPSETASKS_S, ARG_ELAPSETASKS, help = COMMENT_ELAPSETASKS, required = False, nargs=1, default = [DEF_ELAPSETASKS], type=float)

        # Parse de la ligne
        #
        args = parser.parse_args()
        
        # Mode "verbeux"
        self.verbose_ = (False == args.log)

        # Colorisation des affichages ?
        self.color_ = color.colorizer(False if not self.verbose_ else not args.nocolor)

        # Pas de padding ?
        self.noPadding_ = args.nopadding

        # Nettoyage
        self.clear_ = args.clear

        # Mode ajustement
        self.adjust_ = args.adjust

        # Nom du dossier de remplissage
        if args.folder is not None:
            self.folder_ = args.folder[0]
            self.folder_ = os.path.expanduser(self.folder_)   # Remplacer le car. '~' si présent

        # Nombre d'itérations (il y a une valeur par défaut => l'attribut existe donc tjrs !!!)
        self.iterate_ = self.inRange(args.iteration[0], MIN_ITERATE, MAX_ITERATE)

        # Taux de remplissage
        self.fillRate_ = self.inRange(args.fill[0], MIN_FILLRATE, MAX_FILLRATE)
        self.renewRate_ = self.inRange(args.padding[0], MIN_PADDINGRATE, MAX_PADDINGRATE)

        # Profondeur
        self.cleanDepth_ = args.depth[0] if args.depth is not None else -1

        # Nettoyage d'un (ou plusieurs) dossier(s)
        if args.clean is not None:
            self._handleCleanFolders(args.clean)

        # Attentes
        self.waitFiles_ = self.inRange(args.waitfiles[0], MIN_ELAPSEFILES, MAX_ELAPSEFILES)
        self.waitFTasks_ = self.inRange(args.waittasks[0], MIN_ELAPSETASKS, MAX_ELAPSETASKS)

        return True
        
    # Dossier "root"
    def homeFolder():
        return os.path.expanduser(DEF_WIN_ROOT_FOLDER if sys.platform.startswith("win") else DEF_LINUX_ROOT_FOLDER)
    
    # Dossiers de la 'poubelle' de l'agent
    def trashFolders():
        folders = []
        myPlatform = platform.system()
        if  myPlatform == "Windows":
            folders.append("mon-dossier-windows")
        else :
            if myPlatform == "Darwin":
                folders.append("mon-dossier-mac")
            else:
                if myPlatform == "Java":
                    folders.append("mon-dossier-java")
                else:
                    # Pour les Linux / UNIX les dossiers sont à priori les mêmes ...
                    """
                    info = platform.freedesktop_os_release()
                    if info["ID"] == "fedora":
                    """
                    # Les dossiers de la poubelles dans le dossier 'home' de l'utilisateur
                    folders.append(os.path.expanduser("~/.local/share/Trash/files"))
                    folders.append(os.path.expanduser("~/.local/share/Trash/info"))

                    # puis sur tous les volumes "mountés"
                    mountedTrashes = mountPointTrashes(os.getuid())
                    for newTrash in mountedTrashes:
                        folders.append(newTrash)
                    
        return folders
    
    # Affichage de la version de l'application
    #
    def version(self):
        if None == self.color_:
            self.color_ = color.colorizer(True)

        return f"{self.color_.colored(APP_NAME, formatAttr=[color.textAttribute.BOLD], datePrefix=(False == self.verbose_))} par JHB - version {APP_CURRENT_VERSION} du {APP_RELEASE_DATE}"

    #
    # Méthodes à usage interne
    #

    # Liste des dossiers à nettoyer
    def _handleCleanFolders(self, folders):
        # Liste des poubelles
        myTrashFolders = options.trashFolders()

        # Remplacement des valeurs
        destFolders = []
        for folder in folders:
            if FOLDERS_TRASH == folder:
                # On ajoute tous les dossiers de la poubelle
                for tFolder in myTrashFolders:
                    destFolders.append(tFolder)
            else:
                destFolders.append(os.path.expanduser(folder))

        # Les valeurs doivent être uniques ...
        uniqueVals = set(destFolders)
        for val in uniqueVals:
            self.clean_.append(val)

    # Retourne une valeur dans l'intervalle
    def inRange(self, value, min, max):
        return max if value > max else ( min if value < min else value)
# EOF