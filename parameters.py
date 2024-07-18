# coding=UTF-8
#
#   Fichier     :   parameters.py
#
#   Auteur      :   JHB
#
#   Description :   Gestion de la ligne de commande et des constantes
#

import argparse, os, platform
from sharedTools import colorizer as color
from mountPoints import mountPointTrashes

# Nom et version de l'application
APP_NAME = "dCleaner.py"
APP_CURRENT_VERSION = "0.10.3"
APP_RELEASE_DATE = "18/07/2024"
APP_AUTHOR = "GeeHB - j.henrybarnaudiere@gmail.com"

#
# Motif aléatoire
#

# Caractères utilisés pour l'encodage
PATTERN_BASE_STRING = "ABCDEFGKHIJLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/!=@&_-:;,?<>$"

# Taille d'un motif aléatoire en octets
PATTERN_MIN_LEN = 10240
PATTERN_MAX_LEN = 74233

#
# Gestion des fichiers
#

# Nom du sous-dossier
DEF_FOLDER_NAME = ".padding"

# Dossier racine de l'utilisateur courant (fonctionne sous Windows !!!)
DEF_ROOT_FOLDER = "~"

# Taille d'un fichier (en k ou M octets)
FILESIZE_MIN = 1
FILESIZE_MAX = 1024

#
# Dossiers à nettoyer
#
FOLDERS_TRASH = "%trash%"          # La poubelle de l'utilisateur
FOLDERS_TRASH_BIS = "__trash__"
WINDOWS_TRASH = "__wintrash__"     # pour reconnaitre le "dossier" poubelle de Windows

# Constantes générales
#
TIME_PREFIX = "%H:%M:%S "

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

# Nettoyage du dossier de padding
ARG_RECURSE_S = "-r"
ARG_RECURSE   = "--recurse"
COMMENT_RECURSE = "Nettoyage recursif des dossiers et de leurs sous-dossiers"

# Mode "test" - ie. affichages mais pas de suppressions
#   pour "tester" les paramètres
#
ARG_TEST_S = "-t"
ARG_TEST   = "--test"
COMMENT_TEST = "Test des paramètres. Aucun traitement ne sera effectué."

# Paramètres : {arg} {value}
#

# Dossier utilisé pour le remplissage (la partition associée sera saturée)
ARG_FOLDER_S = "-f"
ARG_FOLDER   = "--folder"
COMMENT_FOLDER = "Dossier de remplissage"

# Nettoyage de tous les fichiers et dossiers contenu dans les dossiers sources et ou des fichiers
ARG_CLEANFOLDER_S = "-c"
ARG_CLEANFOLDER   = "--clean"
COMMENT_CLEANFOLDER = "Nettoyage des dossiers et fichiers"

# Profondeur du nettoyage (et de l'effacement des dossiers)
ARG_DEPTH_S = "-d"
ARG_DEPTH   = "--depth"
COMMENT_DEPTH = "Profondeur des dossiers pour la suppression (0 = dossier courant)"

DEF_DEPTH = None    # Par défaut pas de nettoyage en profondeur des dossiers (on ne supprime pas les sous-dossiers)
MIN__DEPTH      = 0
MAX_DEPTH       = 15

# Nombre d'itération à effectuer - Par défaut = 1
ARG_ITERATE_S = "-i"
ARG_ITERATE   = "--iteration"
COMMENT_ITERATE = "Nombre d'itérations du process de nettoyage"

DEF_ITERATE = 1      # Nombre de fois ou sera lancé le processus de remplissage / nettoyage
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
COMMENT_ELAPSEFILES = "Durée en sec. entre 2 suppressions de fichiers"

DEF_ELAPSEFILES = 0.0
MIN_ELAPSEFILES = 0.0
MAX_ELAPSEFILES = 180.0

# Attente entre 2 itérations
ARG_ELAPSETASKS_S = "-wt"
ARG_ELAPSETASKS   = "--waittasks"
COMMENT_ELAPSETASKS = "Durée en sec. entre 2 itérations"

DEF_ELAPSETASKS = 5.0
MIN_ELAPSETASKS = 5.0
MAX_ELAPSETASKS = 180.0

#
# Options d'executions ...
#   le paramètre mode_ est une combianise des différentes valeurs possibles
#
OPTION_INIT    = 0    # Rien à faire
OPTION_TEST    = 1    # On teste ...
OPTION_PADDING = 2    # Remplissage du dossier de 'padding'
OPTION_VERBOSE = 4    # Mode verbeux
OPTION_RECURSE = 8    # Traitement recursif des dossiers

# Valeur par défaut
OPTION_DEFAULT = OPTION_PADDING | OPTION_VERBOSE


#
# Modes de fonctionement
#
MODE_NONE     = 0

MODE_ADJUST     = 1     # Ajustement de la partition
MODE_ADJUST_STR = "ajustement"

MODE_FILL       = 2     # Remplissage de la partition
MODE_FILL_STR   = "remplissage / nettoyage"

MODE_CLEAN      = 4     # Nettoyage de la partition
MODE_CLEAN_STR  = "vidage de dossier"

MODE_CLEAR      = 8     # Vidage
MODE_CLEAR_STR  = "libération"

#
#   classe options : Gestion de la ligne de commande et des paramètres ou options
#
class options(object):

    # Construction
    #
    def __init__(self):

        self.done_ = False

        # Valeurs par défaut
        #
        self.option_ = OPTION_DEFAULT
        self.color_ = None      # Outil de colorisation
        self.adjust_ = False    # Par défaut tous les traitements sont effectués
        self.iterate_ = DEF_ITERATE

        self.fillRate_ = DEF_FILLRATE
        self.renewRate_ = DEF_PADDINGRATE
        self.clear_ = False

        self.waitFiles_ = MIN_ELAPSEFILES
        self.waitTasks_ = MIN_ELAPSETASKS

        self.clean_ = []               # Nettoyage d'un ou plusieurs dossiers
        self.cleanDepth_ = DEF_DEPTH   # Profondeur du nettoyage (pas de suppression)

        # Dossier par défaut
        self.folder_ = os.path.join(options.homeFolder(), DEF_FOLDER_NAME)

        # Liste des dossiers que l'on ne peut supprimer
        #
        self.restricted_ = []
        self.restricted_.append(self.homeFolder())
        trashes = self.trashFolders()
        for trash in trashes:
            self.restricted_.append(trash)

    # Mode verbeux ?
    @property
    def verbose(self):
        return self.__isSet(OPTION_VERBOSE)
    @verbose.setter
    def verbose(self, value):
        self.__set(OPTION_VERBOSE, value)

    # Récursivité ?
    @property
    def recurse(self):
        return self.__isSet(OPTION_RECURSE)
    @recurse.setter
    def recurse(self, value):
        self.__set(OPTION_RECURSE, value)

    # Remplissage ?
    @property
    def padding(self):
        return self.__isSet(OPTION_PADDING)
    @padding.setter
    def padding(self, value):
        self.__set(OPTION_PADDING, value)

    # Test ?
    @property
    def test(self):
        return self.__isSet(OPTION_TEST)
    @test.setter
    def test(self, value):
        self.__set(OPTION_TEST, value)

    # Analyse de la ligne de commandes
    #   returne un booléen
    def parse(self):

        parser = argparse.ArgumentParser(epilog = self.version())

        parser.add_argument(ARG_TEST_S, ARG_TEST, action='store_true', help = COMMENT_TEST, required = False)
        parser.add_argument(ARG_LOGMODE_S, ARG_LOGMODE, action='store_true', help = COMMENT_LOGMODE, required = False)
        parser.add_argument(ARG_NOCOLOR_S, ARG_NOCOLOR, action='store_true', help = COMMENT_NOCOLOR, required = False)
        parser.add_argument(ARG_NOPADDING_S, ARG_NOPADDING, action='store_true', help = COMMENT_NOPADDING, required = False)
        parser.add_argument(ARG_RECURSE_S, ARG_RECURSE, action='store_true', help = COMMENT_RECURSE, required = False)

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
        self.test = args.test

        # Mode "verbeux"
        self.verbose = (False == args.log)

        # Colorisation des affichages ?
        if self.color_ is None:
            self.color_ = color.colorizer(False if not self.verbose else not args.nocolor)
        else:
            self.color_.setColorized(False if not self.verbose else not args.nocolor)

        # Pas de padding ?
        self.padding = (False == args.nopadding)

        # Nettoyage
        self.clear_ = args.clear

        # Récursivité ?
        self.recurse = args.recurse

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
        if not self.recurse and self.cleanDepth_ > 0:
            # Si pas de récursivité, la profondeur max est 0 !
            self.cleanDepth_ = 0

        # Nettoyage d'un (ou plusieurs) dossier(s)
        if args.clean is not None:
            self.handleCleanFolders(args.clean)

        # Attentes
        self.waitFiles_ = self.inRange(args.waitfiles[0], MIN_ELAPSEFILES, MAX_ELAPSEFILES)
        self.waitFTasks_ = self.inRange(args.waittasks[0], MIN_ELAPSETASKS, MAX_ELAPSETASKS)

        return True

    # Dossier "root"
    @staticmethod
    def homeFolder():
        return os.path.expanduser(DEF_ROOT_FOLDER)

    # Dossiers de la 'poubelle' de l'agent
    @staticmethod
    def trashFolders():
        folders = []
        myPlatform = platform.system()
        if  myPlatform == "Windows":
            # Il y a bien un ou plusieurs dossiers Windows mais on ne peut y accéder
            # on ajoute un dossier "bidon" pour pouvoir le faire vider le moment venu
            folders.append(WINDOWS_TRASH)
        else :
            if myPlatform == "Darwin":
                # MacOS
                folders.append(os.path.expanduser("~/.Trash"))
            else:
                # Pour les Linux / UNIX les dossiers sont à priori les mêmes ...
                # Les dossiers de la poubelle dans le dossier 'home' de l'utilisateur
                folders.append(os.path.expanduser("~/.local/share/Trash/files"))
                folders.append(os.path.expanduser("~/.local/share/Trash/info"))

                # ... puis sur tous les volumes "mountés"
                mountedTrashes = mountPointTrashes(os.getuid())
                for newTrash in mountedTrashes:
                    # Les 2 sous dossiers 'files' et 'infos" sont-ils présents ?
                    ntF = os.path.join(newTrash, "files")
                    if os.path.exists(ntF):
                        folders.append(ntF)
                        ntF = os.path.join(newTrash, "infos")
                        if os.path.exists(ntF):
                            folders.append(ntF)
                    else:
                        folders.append(newTrash)

        return folders

    # Affichage de la version de l'application
    #
    #   retourne la chaine caractérisant la version
    #
    def version(self):
        if self.color_ is None:
            self.color_ = color.colorizer(True)

        return f"{self.color_.colored(APP_NAME, formatAttr=[color.textAttribute.BOLD], datePrefix=(False == self.verbose), addPID=(False == self.verbose))} par {APP_AUTHOR} - v{APP_CURRENT_VERSION} du {APP_RELEASE_DATE}"

    # Le dossier a t'il un accès restreint ?
    #
    def isRectrictedAccess(self, folder):

        if folder is not None:
            try:
                return folder in self.restricted_
            except:
                pass

        # Une erreur ? => blocage
        return True

    # Retourne une valeur dans l'intervalle
    def inRange(self, value, min, max):
        return max if value > max else ( min if value < min else value)

    # Liste des dossiers à nettoyer
    def handleCleanFolders(self, folders):
        # Liste des poubelles
        #print("Obtention de la liste des \"dossiers poubelle\"")
        myTrashFolders = options.trashFolders()

        # Remplacement des valeurs
        destFolders = []
        for folder in folders:
            if FOLDERS_TRASH == folder or FOLDERS_TRASH_BIS == folder:
                # On ajoute tous les dossiers de la poubelle
                for tFolder in myTrashFolders:
                    destFolders.append(tFolder)
            else:
                destFolders.append(os.path.expanduser(folder))

        # Les valeurs doivent être uniques ...
        uniqueVals = set(destFolders)
        for val in uniqueVals:
            self.clean_.append(val)

    #
    # Méthodes à usage interne
    #

    # Un bit d'OPTION_VERBOSE est-il positionné ?
    #
    #   bit : Mode(s) ou bit(s) à rechercher
    #
    #   retourne un booléen
    #
    def __isSet(self, bit):
        return (bit == (self.option_ & bit))

    # Positionner ou retirer un bit
    #
    #   bit : bit à positionner ou retirer
    #
    #   set : positionner ? (par défaut True)
    #
    def __set(self, bit, set = True):
        # Déja en place ?
        inPlace = self.__isSet(bit)
        if set:
            if not inPlace:
                # on le met
                self.option_ = self.option_ | bit
        else:
            if inPlace:
               # on le retire
               self.option_ = self.option_ & ~ bit
# EOF
