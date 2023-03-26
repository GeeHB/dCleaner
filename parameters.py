# coding=UTF-8
#
#   Fichier     :   parameters.py
#
#   Auteur      :   JHB
#
#   Description :   Gestion de la ligne de commande et des constantes.
#

from sharedTools import cmdLineParser as parser
from sharedTools import colorizer as color
import sys, os, platform

# Nom et version de l'application
APP_NAME = "dCleaner.py"
APP_CURRENT_VERSION = "0.6.2"
APP_RELEASE_DATE = "22-03-2023"

#
# Valeurs par défaut
#

DEF_PARTITION_FILL_RATE = 80    # Pourcentage de remplissage max. de la partition
DEF_PADDING_RATE = 30           # Dans le % restant, quelle est le taux de renouvellement (ie ce pourcentage sera nettoyé à chaque lancement)

MIN_RATE = 1
MAX_RATE = 95                   # Il faut laisser un peu de place ...
MAX_PADDING_RATE = 50

DEF_ITERATE_COUNT = 1           # Nombre de fois ou sera lancé le processus de remplissage / nettoyage
MIN_ITERATE_COUNT = 1
MAX_ITERATE_COUNT = 100

#
# Motif aléatoire
#

# Caractères utilisés pour l'encodage
PATTERN_BASE_STRING = "ABCDEFGKHIJLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/!=@&_-:;,?<>$"

# Taille d'un motif aléatoire en octets
PATTERN_MIN_LEN = 33
PATTERN_MAX_LEN = 5121

# Gestion des fichiers
#

# Nom du sous-dossier
DEF_FOLDER_NAME = ".padding"

DEF_WIN_ROOT_FOLDER = "c:\\"      # Dossiers par défaut
DEF_LINUX_ROOT_FOLDER = "~"

# Taille d'un fichier (en k ou M octets)
FILESIZE_MIN = 1
FILESIZE_MAX = 1024

# Durée(s) d'attente(s) en sec.
#
MIN_ELAPSE_FILES = 0.0      # Entre la gestion de deux fichiers
MAX_ELAPSE_FILES = 180.0

MIN_ELAPSE_TASKS = 5.0      # Entre 2 tâches en sec.
MAX_ELAPSE_TASKS = 180.0

# Dossiers à nettoyer
#
FOLDERS_SEP = ";"              # Séparateur de liste
FOLDERS_TRASH = "%trash%"      # La poubelle de l'utilisateur

DEF_FOLDER_CLEAN_DEPTH = -1    # Par défaut pas de nettoyage en profondeur des dossiers (on ne supprime pas les sous-dossiers)
MIN_FOLDER_DEPTH       = -1
MAX_FOLDER_DEPTH       = 15

# Commandes reconnues
#

CMD_OPTION_CHAR = "-"                   # Caractère qui précède tjrs un paramètre

CMD_OPTION_LOGMODE = "log"              # Mode non verbeux (spécifique pour les fichiers de logs) - Par défaut Non
CMD_OPTION_NOCOLOR = "nc"               # Pas de colorisation des sorties - Par défaut les sorties seront colorisées
CMD_OPTION_ADJUST = "adjust"            # Effectue uniquement la vérification du dossier de remplissage
CMD_OPTION_FOLDER = "folder"            # Dossier utilisé pour le remplissage (la partition associée sera saturée)

CMD_OPTION_NOPADDING = "np"             # Pas de remplissage (juste nettoyer ou effacer)

CMD_OPTION_ELAPSE_FILES = "waitFiles"   # Attente entre le traitement de 2 fichiers
CMD_OPTION_ELAPSE_TASKS = "waitTasks"   # Attente entre 2 itérations

CMD_OPTION_ITERATE = "i"                # Nombre d'itération à effectuer - Par défaut = 1
CMD_OPTION_PARTITION_FILL_RATE = "fill" # Pourcentage de la partition devant être plein (y compris de padding) - Par défaut 80%
CMD_OPTION_PARTITION_PADDING_RATE = "padding" # Pourcentage restant de la partition à salir à chaque itération - Par défut 30%
CMD_OPTION_CLEAN = "clear"              # Nettoyage du dossier de padding

CMD_OPTION_DEST_FOLDER = "clean"        # Nettoyage de tous les fichiers et dossiers contenu dans le dossier source
CMD_OPTION_DEPTH = "depth"              # Profondeur du nettoyage (et de l'effacement des dossiers)

CMD_OPTION_HELP = "help"                # De l'aide !!!
CMD_OPTION_HELP_MIN = "?"

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
        
        self.iterate_ = DEF_ITERATE_COUNT
        
        self.fillRate_ = DEF_PARTITION_FILL_RATE
        self.renewRate_ = DEF_PADDING_RATE
        self.clear_ = False

        self.waitFiles_ = MIN_ELAPSE_FILES
        self.waitTasks_ = MIN_ELAPSE_TASKS
        
        self.clean_ = []        # Nettoyage d'un ou plusieurs dossiers
        self.cleanDepth_ = DEF_FOLDER_CLEAN_DEPTH   # Profondeur du nettoyage (pas de suppression)

        # Dossier par défaut
        self.folder_ = os.path.join(options.homeFolder(), DEF_FOLDER_NAME)   

    # Analyse de la ligne de commandes
    #   returne un booléen
    def parse(self):

        parameters = parser.cmdLineParser(CMD_OPTION_CHAR)

        # De l'aide ?
        showUsage = ((parameters.NO_INDEX != parameters.findAndRemoveOption(CMD_OPTION_HELP)) or (parameters.NO_INDEX != parameters.findAndRemoveOption(CMD_OPTION_HELP_MIN)))
        
        # Si l'aide est demandée, rien ne sert d'analyser le reste de la ligne de commande
        #
        if False == showUsage:
        
            # En mode log ?
            self.verbose_ = (parameters.NO_INDEX == parameters.findAndRemoveOption(CMD_OPTION_LOGMODE))
            
            # Colorisation des affichages ?
            noColor = (parameters.NO_INDEX != parameters.findAndRemoveOption(CMD_OPTION_NOCOLOR)) if self.verbose_ else True

            # Création de l'objet pour la gestion de la colorisation
            self.color_ = color.colorizer(False == noColor)

            # Pas de padding ?
            self.noPadding_ = (parameters.NO_INDEX != parameters.findAndRemoveOption(CMD_OPTION_NOPADDING)) 

            # Nettoyage ?
            self.clear_ = (parameters.NO_INDEX != parameters.findAndRemoveOption(CMD_OPTION_CLEAN))

            if False == self.clear_:
                # Ajustement ?
                self.adjust_ = (parameters.NO_INDEX != parameters.findAndRemoveOption(CMD_OPTION_ADJUST))

            # Nom du dossier de remplissage
            res = parameters.getOptionValue(CMD_OPTION_FOLDER)
            if None != res and None != res[0]:
                self.folder_ = res[0]
            self.folder_ = os.path.expanduser(self.folder_)   # Remplacer le car. '~' si présent

             # Nettoyage d'un (ou plusieurs) dossier(s)
            res = parameters.getOptionValue(CMD_OPTION_DEST_FOLDER)
            if None != res and None != res[0]:
                self._handleCleanFolders(res[0])

           # Nombre d'itérations
            res = parameters.getOptionValueNum(CMD_OPTION_ITERATE, min = MIN_ITERATE_COUNT, max = MAX_ITERATE_COUNT)
            if None != res[0]:
                self.iterate_ = res[0]
                
           # Attente entre 2 (suppressions) de fichier
            res = parameters.getOptionValueNum(CMD_OPTION_ELAPSE_FILES, MIN_ELAPSE_FILES, MAX_ELAPSE_TASKS)
            if None != res[0]:
                self.waitFiles_ = res[0]

            # Attente entre 2 séries de traitement
            res = parameters.getOptionValueNum(CMD_OPTION_ELAPSE_TASKS, MIN_ELAPSE_TASKS, MAX_ELAPSE_TASKS)
            if None != res[0]:
                self.waitTasks_ = res[0]
           
           # Profondeur
            res = parameters.getOptionValueNum(CMD_OPTION_DEPTH, MIN_FOLDER_DEPTH, MAX_FOLDER_DEPTH)
            if None != res[0]:
                self.cleanDepth_ = int(res[0]) # C'est un nombre entier

            if False == self.clear_:
                # Taux de remplissage permanent de la partition
                res = parameters.getOptionValueNum(CMD_OPTION_PARTITION_FILL_RATE, MIN_RATE, MAX_RATE)
                if None != res[0]:
                    self.fillRate_ = res[0]

                # Taux de remplissage du reste de la partition
                res = parameters.getOptionValueNum(CMD_OPTION_PARTITION_PADDING_RATE, MIN_RATE, MAX_PADDING_RATE)
                if None != res[0]:
                    self.renewRate_ = res[0]

        # A priori il ne devrait plus y avoir de paramètres
        """
        a = parameters.size()            # Elements dans la ligne de cmd
        b = parameters.options()         # Options non traitées
        c = parameters.usefullItems()    # Elements restants (non traités) 
        """
        # Une erreur, trop de paramètres ou rien à faire ...
        if True == showUsage or parameters.usefullItems() > 0 or (self.noPadding_ and self.clear_ == False and self.clean_ is None):
            self.usage()
            return False

        # Ok
        return True

    # Affichage de l'usage
    #
    def usage(self, fullUsage = True):
        if None == self.color_:
            self.color_ = color.colorizer(True)

        print(self.color_.colored(APP_NAME, formatAttr=[color.textAttribute.BOLD], datePrefix=(False == self.verbose_)), "par JHB - version", APP_CURRENT_VERSION, "du", APP_RELEASE_DATE)

        if self.verbose_:
            print("")
            
        # Show all commands ?
        if True == fullUsage:
            print("\t", self.color_.colored("[ " + CMD_OPTION_CHAR + CMD_OPTION_HELP + " ou " + CMD_OPTION_CHAR + CMD_OPTION_HELP_MIN + " ]", formatAttr=[color.textAttribute.DARK]), ": Aide")
            print("\t", self.color_.colored("[ " + CMD_OPTION_CHAR + CMD_OPTION_FOLDER + " {dossier} ]", formatAttr=[color.textAttribute.DARK]), ": Chemin du dossier de remplissage")
            print("\t", self.color_.colored("[ " + CMD_OPTION_CHAR + CMD_OPTION_DEST_FOLDER + " {dossiers} ]", formatAttr=[color.textAttribute.DARK]), ": Nettoyage du ou des dossiers")
            print("\t", self.color_.colored("[ " + CMD_OPTION_CHAR + CMD_OPTION_DEPTH + " {n} ]", formatAttr=[color.textAttribute.DARK]), ": Suppression des dossiers en profondeur (à partir de)")
            print("\t", self.color_.colored("[ " + CMD_OPTION_CHAR + CMD_OPTION_NOCOLOR + " ]", formatAttr=[color.textAttribute.DARK]), ": Affichages non colorisés")
            print("\t", self.color_.colored("[ " + CMD_OPTION_CHAR + CMD_OPTION_NOPADDING + " ]", formatAttr=[color.textAttribute.DARK]), ": Pas de remplissage de la partition")
            print("\t", self.color_.colored("[ " + CMD_OPTION_CHAR + CMD_OPTION_LOGMODE + " ]", formatAttr=[color.textAttribute.DARK]), ": Mode non verbeux, pour les fichiers de logs")
            print("\t", self.color_.colored("[ " + CMD_OPTION_CHAR + CMD_OPTION_CLEAN + " ]", formatAttr=[color.textAttribute.DARK]), ": Nettoyage du dossier de remplissage")
            print("\t", self.color_.colored("[ " + CMD_OPTION_CHAR + CMD_OPTION_ADJUST + " ]", formatAttr=[color.textAttribute.DARK]), ": Ajustement du dossier de remplissage")
            print("\t", self.color_.colored("[ " + CMD_OPTION_CHAR + CMD_OPTION_ITERATE + " {nombre} ]",formatAttr=[color.textAttribute.DARK]),": Nombre d'itération du process de nettoyage")
            print("\t", self.color_.colored("[ " + CMD_OPTION_CHAR + CMD_OPTION_PARTITION_FILL_RATE + " {%} ]",formatAttr=[color.textAttribute.DARK]),": Taux de remplissage de la partition")
            print("\t", self.color_.colored("[ " + CMD_OPTION_CHAR + CMD_OPTION_PARTITION_PADDING_RATE + " {%} ]", formatAttr=[color.textAttribute.DARK]),": Taille (en % de la taille libre) à nettoyer")
            print("\t", self.color_.colored("[ " + CMD_OPTION_CHAR + CMD_OPTION_ELAPSE_FILES + " {n} ]", formatAttr=[color.textAttribute.DARK]), ": durée en s. entre 2 suppressions de fichiers")
            print("\t", self.color_.colored("[ " + CMD_OPTION_CHAR + CMD_OPTION_ELAPSE_TASKS + " {n} ]", formatAttr=[color.textAttribute.DARK]), ": durée en s. entre 2 itérations")
    
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
                    info = platform.freedesktop_os_release()
                    if info["ID"] == "fedora":
                        # ouf il y en a 2
                        folders.append(os.path.expanduser("~/.local/share/Trash/files"))
                        folders.append(os.path.expanduser("~/.local/share/Trash/info"))
                    else:
                        folders.append("mon-dossier-linux")
        return folders

    #
    # Méthodes à usage interne
    #

    # Liste des dossiers à nettoyer
    def _handleCleanFolders(self, fList):
        # Liste des dossiers
        folders = fList.split(FOLDERS_SEP)

        destFolders = []
        myTrashFolders = options.trashFolders()

        # Remplacement des valeurs
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

# EOF