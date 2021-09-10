# coding=UTF-8
#
#   Fichier     :   parameters.py
#
#   Author      :   JHB
#
#   Description :   Gestion de la ligne de commande et des constantes.
#
#   Version     :   0.2.3
#
#   Date        :   10 septembre 2021
#

from cmdLineParser import cmdLineParser
from colorizer import colorizer, textAttribute

#
# Valeurs par défaut
#

CURRENT_VERSION = "version 0.2.3"

DEF_PARTITION_FILL_RATE = 80    # Pourcentage de remplissage max. de la partition
DEF_PADDING_RATE = 30           # Dans le % restant, quelle est le taux de renouvellement (ie ce pourcentage sera nettoyé à chaque lancement)

MIN_RATE = 1
MAX_RATE = 95                   # Il faut laisser un peu de place ...
MAX_PADDING_RATE = 50

DEF_ITERATE_COUNT = 1           # Nombre de fois ou sera lancé le processus de remplissage / nettoyage
MIN_ITERATE_COUNT = 1
MAX_ITERATE_COUNT = 100

# Motif aléatoire
#

# Caractères utilisés pour l'encodage
PATTERN_BASE_STRING = "ABCDEFGKHIJLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/!=@&_-:;,?<>$"

# Taille d'un motif aléatoire en octets
PATTERN_MIN_LEN = 33
PATTERN_MAX_LEN = 5121

# Gestion des fichiers
#

# Taille d'un fichier (en k ou M octets)
FILESIZE_MIN = 1
FILESIZE_MAX = 1024

# Durée(s) d'attente(s) en sec.
#
MIN_ELPASE_FILES = 0.1      # Entre la gestion de deux fichiers
MIN_ELAPSE_TASKS = 900      # Entre 2 tâches

# Commandes reconnues
#

CMD_OPTION_CHAR = "-"                   # Caractère qui précède tjrs un paramètre

CMD_OPTION_LOGMODE = "log"              # Mode non verbeux (spécifique pour les fichiers de logs) - Par défaut Non
CMD_OPTION_NOCOLOR = "nc"               # Pas de colorisation des sorties - Par défaut les sorties seront colorisées
CMD_OPTION_ADJUST = "adjust"            # Effectue uniquement la vérification du dossier de remplissage
CMD_OPTION_FOLDER = "folder"            # Dossier utilisé pour le remplissage (la partition associée sera saturée)
CMD_OPTION_ITERATE = "i"                # Nombre d'itération à effectuer - Par défaut = 1
CMD_OPTION_PARTITION_FILL_RATE = "fill" # Pourcentage de la partition devant être plein (y compris de padding) - Par défaut 80%
CMD_OPTION_PARTITION_PADDING_RATE = "padding" # Pourcentage restant de la partition à salir à chaque itération - Par défut 30%
 
#
#   options object : command-line parsing and parameters management
#
class options(object):

    # Construction
    #
    def __init__(self):

        # Valeurs par défaut
        self.color_ = None      # Outil de colorisation
        self.verbose_ = True    # Par défaut l'application trace tout ...
        self.adjust_ = False    # Par défaut tous les traitements sont effectués
        self.folder_ = ""
        self.iterate_ = DEF_ITERATE_COUNT
        self.fillRate_ = DEF_PARTITION_FILL_RATE
        self.renewRate_ = DEF_PADDING_RATE

    # Analyse de la ligne de commandes
    #   returne un booléen
    def parse(self):

        showUsage = False
        parameters = cmdLineParser(CMD_OPTION_CHAR)
        if 0 == parameters.size():
            showUsage = True
        else:
            # En mode log ?
            self.verbose_ = (parameters.NO_INDEX == parameters.findAndRemoveOption(CMD_OPTION_LOGMODE))
            
            # Colorisation des affichages ?
            noColor = (parameters.NO_INDEX != parameters.findAndRemoveOption(CMD_OPTION_NOCOLOR)) if self.verbose_ else True
            
            # Création de l'objet pour la gestion de la colorisation
            self.color_ = colorizer(False == noColor)

            # Ajustement ?
            self.adjust_ = (parameters.NO_INDEX != parameters.findAndRemoveOption(CMD_OPTION_ADJUST))

            # Nom du dossier
            res = parameters.getOptionValue(CMD_OPTION_FOLDER)
            if None == res[0]:
                # Le dossier est obligatoire
                showUsage = True
            else:
                
                self.folder_ = res[0]
                
                # Nombre d'itérations
                res = parameters.getOptionValueNum(CMD_OPTION_ITERATE, min = MIN_ITERATE_COUNT, max = MAX_ITERATE_COUNT)
                if None != res[0]:
                    self.iterate_ = res[0]
                
                # Taux de remplissage permanent de la partition
                res = parameters.getOptionValueNum(CMD_OPTION_PARTITION_FILL_RATE, MIN_RATE, MAX_RATE)
                if None != res[0]:
                    self.fillRate_ = res[0]

                # Taux de remplissage du reste de la partition
                res = parameters.getOptionValueNum(CMD_OPTION_PARTITION_PADDING_RATE, MIN_RATE, MAX_PADDING_RATE)
                if None != res[0]:
                    self.renewRate_ = res[0]

        # A priori il ne devrait plus y avoir de paramètres
        if True == showUsage or parameters.options() > 0 :
            self.usage()
            return False
        
        # Ok
        return True

    # Affichage de l'usage
    #
    def usage(self, fullUsage = True):
        if None == self.color_:
            self.color_ = colorizer(True)

        print(self.color_.colored("dCleaner.py", formatAttr=[textAttribute.BOLD], datePrefix=(False == self.verbose_)), "par JHB -", CURRENT_VERSION)

        if self.verbose_:
            print("")
            
        # Show all commands ?
        if True == fullUsage:
            print("\t", self.color_.colored("  " + CMD_OPTION_CHAR + CMD_OPTION_FOLDER + " {dossier} ", formatAttr=[textAttribute.DARK]), ": Dossier pour les fichiers de remplisage")
            print("\t", self.color_.colored("[ " + CMD_OPTION_CHAR + CMD_OPTION_NOCOLOR + " ]", formatAttr=[textAttribute.DARK]), ": Affichages non colorisés")
            print("\t", self.color_.colored("[ " + CMD_OPTION_CHAR + CMD_OPTION_LOGMODE + " ]", formatAttr=[textAttribute.DARK]), ": Mode non verbeux, pour les fichiers de logs")
            print("\t", self.color_.colored("[ " + CMD_OPTION_CHAR + CMD_OPTION_ADJUST + " ]", formatAttr=[textAttribute.DARK]), ": Ajustement du dossier de remplissage.")
            print("\t", self.color_.colored("[ " + CMD_OPTION_CHAR + CMD_OPTION_ITERATE + " {nombre} ]",formatAttr=[textAttribute.DARK]),": Nombre d'itération du process de nettoyage")
            print("\t", self.color_.colored("[ " + CMD_OPTION_CHAR + CMD_OPTION_PARTITION_FILL_RATE + " {nombre} ]",formatAttr=[textAttribute.DARK]),": Taux de remplissage de la partition")
            print("\t", self.color_.colored("[ " + CMD_OPTION_CHAR + CMD_OPTION_PARTITION_PADDING_RATE + " ]", formatAttr=[textAttribute.DARK]),": Taille (en %) de la zone à nettoyer")

# EOF