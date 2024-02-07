# coding=UTF-8
#
#   Fichier     :   colorizer.py
#
#   Description :   Définition des objets :
#                     - colorizer : Gestion de la colorisation des sorties enmode terminal (et/ou texte)
#                     - textAttribute : Liste des attributs
#                     - textColor : Liste des couleurs de texte
#                     - backColor : Liste des couleurs de fond
#
#   Commentaire :  le module termcolor doit être installé (pip install termcolor)
#

try :
    # Pour la coloration des sorties terminal
    from termcolor import colored
    packageTermColor__ = True
except ModuleNotFoundError:
    packageTermColor__ = False

# Pour l'ajout de la date et de l'heure en mode "logs
from datetime import datetime

# Format de la date (pour les logs)
#
LOG_DATE_FORMAT = "[%d/%m/%Y - %H:%M:%S] "

# Messages d'erreur
#
MSG_NO_TERM_COLOR = "Attention - le package termcolor (python-termcolor) n'est pas installé"
#MSG_NO_TERM_COLOR = "Warning - termcolor package (python-termcolor) is not installed"

#
# backColor - Couleurs de fond
#
class backColor:

    GREY = GRIS = "on_grey"
    RED = ROUGE = "on_red"
    GREEN = VERT = "on_green"
    YELLOW = JAUNE = "on_yellow"
    BLUE = BLEU = "on_blue"
    MAGENTA = "on_magenta"
    CYAN = "on_cyan"
    WHITE = BLANC = "on_white"

#
# textkColor - Couleurs du texte
#
class textColor:

    GREY = GRIS = "grey"
    RED = ROUGE = "red"
    GREEN = VERT = "green"
    YELLOW = JAUNE = "yellow"
    BLUE = BLEU = "blue"
    MAGENTA = "magenta"
    CYAN = "cyan"
    WHITE = BLANC = "white"

#
# colorAttribute - Attributs d'affichage
#
class textAttribute:
    BOLD = GRAS = "bold"
    DARK = FONCE = "dark"
    UNDERLINE = SOULIGNE = "underline"
    BLINK = CLIGNOTANT = "blink"
    REVERSE = INVERSE = "reverse"
    CONCELED = CACHE = "concealed"

#
#   colorizer  - Colorisation du texte
#
class colorizer:
    
    colored_ = False       # Doit-on coloriser ?

    # Construction
    def __init__(self, colored = True, message = True):
        self.setColorized(packageTermColor__ if None == colored else colored, message)
                        
    # Mise en place de la colorisation
    def setColorized(self, colored = True, message = None):
        self.colored_ = colored

        if True == colored and False == packageTermColor__:
            self.colored_ = False
            if message is not None:
                print(MSG_NO_TERM_COLOR)
    
    # Formatage d'une ligne de texte
    #   Retourne la chaine complète
    def colored(self, text, txtColor = None, bkColor = None, formatAttr = None, datePrefix = False):
        
        prefix = ""
        if datePrefix:
            # En mode log. on ajoute la date et l'heure
            today = datetime.now()
            prefix = today.strftime(LOG_DATE_FORMAT)
        
        # On colorise ou pas ...
        return prefix + (colored(text, color=txtColor, on_color = bkColor, attrs = formatAttr) if True == self.colored_ else text)

    # Début de ligne en mode [OK] / [KO]
    def checkBoxLine(self, checked = True, text = "", color = None, prefix = ""):
        box=prefix + "["
        if True == checked:
            box+=self.colored("OK", textColor.VERT)
        else:
            box+=self.colored("KO", textColor.ROUGE if color == None else color)
        box+="]"
        if len(text) > 0 :
            box+=" "
            box+=text
        return box
# EOF