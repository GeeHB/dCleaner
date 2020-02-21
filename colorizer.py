# coding=UTF-8
#
#   Fichier     :   colorizer.py
#
#   Auteur      :   JHB
#
#   Description :   Définition des objets :
#                     - colorizer : Gestion de la colorisation des sorties enmode terminal (et/ou texte)
#                     - textAttribute : Liste des attributs
#                     - textColor : Liste des couleurs de texte
#                     - backColor : Liste des coleurs de fond
#
#   Remarque    :  
#
#   Version     :   1.5.6
#
#   Date        :   20 février 2020
#

from termcolor import colored               # Pour la coloration des sorties terminal

#
# backColor - Couleurs de fonc
#
class backColor:

    GRIS = "on_grey"
    ROUGE = "on_red"
    VERT = "on_green"
    JAUNE = "on_yellow"
    BLEU = "on_blue"
    MAGENTA = "on_magenta"
    CYAN = "on_cyan"
    BLANC = "on_white"

#
# textkColor - Couleurs de fonc
#
class textColor:

    GRIS = "grey"
    ROUGE = "red"
    VERT = "green"
    JAUNE = "yellow"
    BLEU = "blue"
    MAGENTA = "magenta"
    CYAN = "cyan"
    BLANC = "white"

#
# colorAttribute - Attbiuts d'affichage
#
class textAttribute:
    GRAS = "bold"
    FONCE = "dark"
    SOULIGNE = "underline"
    CLIGNTANT = "blink"
    INVERSE = "reverse"
    CACHE = "concealed"

#
#   textColor  - Colorisation du texte
#
class colorizer:
    # Données membres
    #
    colored_ = True       # Doit-on coloriser ? Par défaut oui ...
    
    # Construction
    def __init__(self, colored = True):
        self.colored_ = colored

    # Formatage d'une ligne de texte
    def colored(self, text, txtColor = None, bkColor = None, formatAttr = None):
        # On colorise ou pas ...
        return colored(text, color=txtColor, on_color = bkColor, attrs = formatAttr) if True == self.colored_ else text

# EOF