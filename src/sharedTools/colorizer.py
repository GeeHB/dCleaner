#!/bin/python
# pyright: reportPossiblyUnboundVariable= none
#
# coding=UTF-8
#
#   Fichier     :   colorizer.py
#
#   Description :   Définition des objets :
#                     - colorizer : Gestion de la colorisation des sorties en mode terminal (et/ou texte)
#                     - textAttribute : Liste des attributs
#                     - textColor : Liste des couleurs de texte
#                     - backColor : Liste des couleurs de fond
#
#   Commentaire :  le module termcolor doit être installé (pip install termcolor)
#

COLORIZER_VERSION = "2.1.1"

try :
    # Pour la coloration des sorties terminal
    import termcolor
    packageTermColor__ = True
except ModuleNotFoundError:
    packageTermColor__ = False

# Messages d'erreur
#
MSG_NO_TERM_COLOR = "Attention - le package termcolor (python-termcolor) n'est pas installé . Utilisez pip install termcolor"
#MSG_NO_TERM_COLOR = "Warning - termcolor package (python-termcolor) is not installed"

#
# backColor - Couleurs de fond
#
class backColor:
    GREY:str = "on_grey"
    GRIS:str = GREY

    RED:str = "on_red"
    ROUGE:str = RED

    GREEN:str = "on_green"
    VERT:str = GREEN

    YELLOW:str = "on_yellow"
    JAUNE:str = YELLOW

    BLUE:str = "on_blue"
    BLEU:str = BLUE

    MAGENTA:str = "on_magenta"

    CYAN:str = "on_cyan"

    WHITE:str = "on_white"
    BLANC:str = WHITE

#
# textkColor - Couleurs du texte
#
class textColor:
    GREY:str = "grey"
    GRIS:str = GREY

    RED:str = "red"
    ROUGE:str = RED

    GREEN:str = "green"
    VERT:str = GREEN

    YELLOW:str = "yellow"
    JAUNE:str = YELLOW

    BLUE:str = "blue"
    BLEU:str = BLUE

    MAGENTA:str = "magenta"

    CYAN:str = "cyan"

    WHITE:str = "white"
    BLANC:str = WHITE

#
# colorAttribute - Attributs d'affichage
#
class textAttribute:
    BOLD:str = "bold"
    GRAS:str = BOLD

    DARK:str = "dark"
    FONCE:str = DARK

    UNDERLINE:str = "underline"
    SOULIGNE:str = UNDERLINE

    BLINK:str = "blink"
    CLIGNOTANT:str = BLINK

    REVERSE:str = "reverse"
    INVERSE:str = REVERSE

    CONCEALED:str = "concealed"
    CACHE:str = CONCEALED

#
#   colorizer  - Colorisation du texte
#
class colorizer:
    # Construction
    def __init__(self, colored:bool | None = True, _message:bool = True):
        self.colored_:bool = False       # Doit-on coloriser ?
        self.setColorized(packageTermColor__ if colored is None else colored)

    # Mise en place de la colorisation
    def setColorized(self, colored:bool = True, message:str | None = None):
        self.colored_ = colored

        if True == colored and False == packageTermColor__:
            self.colored_ = False
            print(MSG_NO_TERM_COLOR if message is None else message)

    # Formatage d'une ligne de texte
    #   Retourne la chaine complète
    def colored(self, content:str, txtColor:str | None, bkColor: str | None = None, formatAttr : str | None = None) -> str:
        retour:str = content
        if self.colored_:
            retour = termcolor.colored(text=content, color=txtColor, on_color = bkColor, attrs = formatAttr)
        return retour

    # Début de ligne en mode [OK] / [KO]
    def checkBoxLine(self, checked:bool = True, text:str = "", color: str | None = None):
        box:str = "["
        if True == checked:
            box+=self.colored("OK", textColor.VERT)
        else:
            box+=self.colored("KO", txtColor = textColor.ROUGE if color is None else color)
        box+="]"
        if len(text) > 0 :
            box+=" "
            box+=text
        return box
# EOF
